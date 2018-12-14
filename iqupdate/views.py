from flask import url_for, render_template, request
from flask_security import Security, SQLAlchemyUserDatastore
import flask_admin
from flask_admin import helpers as admin_helpers
from flask_babelex import lazy_gettext as _
from iqupdate import db
from iqupdate.models import Role, User, ServicePack, ServicePackDetail
from iqupdate.forms import MyModelView, ServicePackAdmin


def init_views(application):
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(application, user_datastore)

    # Flask views
    @application.route('/iq7/v1/updates')
    def updates_view():
        has_updates_for = request.args.get('hasUpdatesFor')
        greater_than = request.args.get('greaterThan')
        version_number = 0
        if has_updates_for:
            version_number = int(has_updates_for)
        elif greater_than:
            version_number = int(greater_than)
        service_packs = ServicePack.query.order_by(ServicePack.release_date).filter(
            ServicePack.version_number > version_number).all()
        if has_updates_for:
            return 'true' if len(service_packs) > 0 else 'false'
        newest = service_packs[-1].version_number if len(service_packs) > 0 else None
        return render_template('service_packs.html', service_packs=service_packs,
                               newest_version_number=newest)

    @application.route('/iq7/v1/updates/<version_number>')
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

    @application.errorhandler(403)
    def forbidden(error):
        """
        render to 403.html
        :return:
        """
        application.logger.info(error)
        return render_template('403.html'), 403

    @application.errorhandler(404)
    def page_not_found(error):
        """
        render to 404.html
        :return:
        """
        application.logger.info(error)
        return render_template('404.html'), 404

    @application.errorhandler(500)
    def internal_server_error(error):
        """
        render to 500.html
        :return:
        """
        db.session.rollback()
        application.logger.info(error)
        return render_template('500.html'), 500

    # Create admin
    admin = flask_admin.Admin(
        application,
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

    return application
