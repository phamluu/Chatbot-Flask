from flask import Blueprint, request
from app.services.faq_service import (
    render_faq_list,
    handle_post_faq,
    handle_update_faq,
    handle_delete_faq
)

faq_bp = Blueprint('faq', __name__)

@faq_bp.route('/faq', methods=['GET'])
def manage_faq():
    return render_faq_list()

@faq_bp.route('/post-faq', methods=['POST'])
def post_faq():
    return handle_post_faq(request)

@faq_bp.route('/faq/update/<int:id>', methods=['POST'])
def update_faq(id):
    return handle_update_faq(id, request)

@faq_bp.route('/faq/delete/<int:id>', methods=['POST'])
def delete_faq(id):
    return handle_delete_faq(id)
