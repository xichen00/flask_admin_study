from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, current_user
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_babelex import Babel, lazy_gettext as _

app = Flask(__name__)
babel = Babel(app)
app.config.from_pyfile('iq_update_config.py')
db = SQLAlchemy(app)


@babel.localeselector
def get_locale():
    """
    Get the local language from user's browser.
    :return: A list with ['en', 'zh', 'de', 'fr']
    """
    return request.accept_languages.best_match(['de', 'fr', 'en', 'zh'])


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class ServicePack(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(20), unique=True, nullable=False)
    version_number = db.Column(db.Integer(), unique=True, nullable=False)
    release_date = db.Column(db.Date(), nullable=False)

    def __str__(self):
        return "{} - {}".format(self.description, self.release_date)


class ServicePackDetail(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    language = db.Column(db.Enum('de', 'en'), nullable=False)
    contents = db.Column(db.Text, nullable=False)
    service_pack_id = db.Column(db.Integer, db.ForeignKey(ServicePack.id), nullable=False)
    service_pack = db.relation(ServicePack, backref='details')

    def __str__(self):
        return "{} - {}".format(self.language, self.contents)

    def __repr__(self):
        return self.__str__


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


# Inline form for ServicePack and ServicePackDetail
inline_form_options = {
    'form_label': "Details",
    'form_columns': ['id', 'language', 'contents'],
    'form_args': None,
    'form_extra_fields': None,
}


# ServicePackAdmin model
class ServicePackAdmin(MyModelView):
    form_excluded_columns = ('version_number',)
    inline_models = [(ServicePackDetail, inline_form_options), ]
    column_list = [
        'description',
        'release_date',
    ]
    column_default_sort = ('release_date', True)

    def __init__(self):
        super(ServicePackAdmin, self).__init__(ServicePack, db.session, name='ServicePacks')

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('releaseuser'):
            return True

        return False

    def on_model_change(self, form, service_pack, is_created):
        description = service_pack.description
        service_pack.version_number = int(description.split(' ')[-1])

        return service_pack

    def on_model_delete(self, service_pack):
        ServicePackDetail.query.filter_by(service_pack_id=service_pack.id).delete()
        db.session.commit()
        return service_pack


# Flask views
@app.route('/iq7/v1/updates')
def updates_view():
    has_updates_for = request.args.get('hasUpdatesFor')
    greater_then = request.args.get('greaterThen')
    version_number = 0
    if has_updates_for:
        version_number = int(has_updates_for)
    elif greater_then:
        version_number = int(greater_then)
    service_packs = ServicePack.query.order_by(ServicePack.release_date).filter(
        ServicePack.version_number > version_number).all()
    newest = service_packs[-1]
    if newest:
        newest_version_number = newest.version_number
    if has_updates_for:
        if len(service_packs) >= 1:
            return 'true'
        else:
            return 'false'
    return render_template('service_packs.html', service_packs=service_packs,
                           newest_version_number=newest_version_number)


@app.route('/iq7/v1/updates/<version_number>')
def service_pack_info_view(version_number):
    language = request.args.get('language')
    if language is None:
        language = request.accept_languages.best_match(['en', 'zh', 'de', 'fr'])
    if language != 'de':
        language = 'en'
    back_url = request.referrer
    if back_url is None:
        back_url = '/iq7/v1/updates'
    service_pack = ServicePack.query.filter_by(version_number=int(version_number)).first()
    contents = ''
    if service_pack:
        detail = ServicePackDetail.query.filter(ServicePackDetail.service_pack_id == service_pack.id,
                                                ServicePackDetail.language == language).first()
        if detail:
            contents = detail.contents
    back_html = '<p><a href="' + back_url + '">' + _(u'Back') + '</a></p>'
    return '{}{}'.format(contents, back_html)


@app.errorhandler(403)
def forbidden(arg1):
    """
    render to 403.html
    :return:
    """
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(arg1):
    """
    render to 404.html
    :return:
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(arg1):
    """
    render to 500.html
    :return:
    """
    return render_template('500.html'), 500


# Create admin
admin = flask_admin.Admin(
    app,
    'APIS Release',
    base_template='my_master.html',
    template_mode='bootstrap3',
)

# Add model views
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(User, db.session))
admin.add_view(ServicePackAdmin())


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


if __name__ == '__main__':
    # Start app
    app.run(host='0.0.0.0', port=5000, debug=True)
