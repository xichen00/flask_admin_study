from flask import url_for, redirect, request, abort
from flask_security import current_user
from flask_admin.contrib import sqla
from iqupdate import db as database
from iqupdate.models import ServicePack, ServicePackDetail


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
        super(ServicePackAdmin, self).__init__(ServicePack, database.session, name='ServicePacks')

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
        database.session.commit()
        return service_pack
