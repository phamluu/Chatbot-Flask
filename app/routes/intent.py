from flask_security import roles_required, login_required
from flask import Blueprint, request

from app.services.intent_service import (
    handle_delete_intent, handle_delete_intent_response, 
    handle_manage_intent, handle_manage_intent_input,
      handle_manage_intent_response, handle_update_intent, 
      handle_update_intent_input, handle_update_intent_response
)

intent_bp  = Blueprint('intent', __name__) #endpoint: chatbot_api

# intent management routes
@intent_bp.route("/intent", methods=['GET', 'POST'])
@roles_required('admin')
def manage_intent():
    return handle_manage_intent(request)
@intent_bp.route('/intent/update/<int:id>', methods=['POST'])
@roles_required('admin')
def update_intent(id):
    return handle_update_intent(id, request)


@intent_bp.route('/intent/delete/<int:id>', methods=['POST'])
@roles_required('admin')
def delete_intent(id):
    return handle_delete_intent(id)
#end

# intent input management routes
@intent_bp.route("/intent_input/<int:intent_id>", methods=['GET', 'POST'])
@roles_required('admin')
def manage_intent_input(intent_id):
    return handle_manage_intent_input(request, intent_id)

@intent_bp.route('/intent_input/update/<int:id>', methods=['POST'])
@roles_required('admin')
def update_intent_input(id):
    return handle_update_intent_input(id, request)

@intent_bp.route('/intent_input/delete/<int:id>', methods=['POST'])
@roles_required('admin')
def delete_intent_input(id):
    return handle_delete_intent(id)
#end

# intent response management routes
@intent_bp.route("/intent_response/<int:intent_id>", methods=["GET", "POST"])
@roles_required('admin')
def manage_intent_responses(intent_id):
    return handle_manage_intent_response(request, intent_id)

@intent_bp.route('/intent_response/update/<int:id>', methods=['POST'])
@roles_required('admin')
def update_intent_responses(id):
    return handle_update_intent_response(id, request)

@intent_bp.route('/intent_response/delete/<int:id>', methods=['POST'])
@roles_required('admin')
def delete_intent_responses(id):
    return handle_delete_intent_response(id)
#end