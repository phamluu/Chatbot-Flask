from flask_security import roles_required, login_required
from flask import Blueprint, request
from app.services.user_service import (
    handle_manage_user,
    handle_update_user,
    handle_delete_user,
    handle_index,
    handle_chat_post
)

user_bp = Blueprint('user', __name__)

@user_bp.route('/user', methods=['GET', 'POST'])
@roles_required('admin')
def manage_user():
    return handle_manage_user(request)

@user_bp.route('/user/update/<int:id>', methods=['POST'])
@roles_required('admin')
def update_user(id):
    return handle_update_user(id, request)

@user_bp.route('/user/delete/<int:id>', methods=['POST'])
@roles_required('admin')
def delete_user(id):
    return handle_delete_user(id)

@user_bp.route('/chat-user')
def index():
    return "Hello World"
    #return handle_index()

@user_bp.route('/chat_post', methods=['POST'])
def chat_post():
    return handle_chat_post(request)
