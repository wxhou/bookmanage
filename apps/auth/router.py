from flask import Blueprint
from common.extensions import docs
from . import views_admin

# bp_auth
bp_auth = Blueprint('bp_auth', __name__)
bp_auth.register_blueprint(views_admin.bp_admin)




def register_auth_docs():
    docs.register(views_admin.upload_avatar,
                  blueprint='bp_auth.bp_admin')
    docs.register(views_admin.login,
                  blueprint='bp_auth.bp_admin')
    docs.register(views_admin.logout,
                  blueprint='bp_auth.bp_admin')
    docs.register(views_admin.active_user,
                  blueprint='bp_auth.bp_admin')
    docs.register(views_admin.UserView,
                  endpoint='UserView',
                  blueprint='bp_auth.bp_admin')
    docs.register(views_admin.UserEditView,
                  endpoint='UserEditView',
                  blueprint='bp_auth.bp_admin')