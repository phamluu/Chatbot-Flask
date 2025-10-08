import subprocess
import sys
from flask_security import roles_required, login_required
from flask import Blueprint, flash, jsonify, redirect, request, url_for

from app.services.intent_service import (
    handle_delete_intent, handle_delete_intent_response, 
    handle_manage_intent, handle_manage_intent_input,
      handle_manage_intent_response, handle_update_intent, 
      handle_update_intent_input, handle_update_intent_response
)

intent_bp  = Blueprint('intent', __name__) #endpoint

@intent_bp.route("/intent/train", methods=["POST"])
@roles_required('admin')
def train_intent():
    import time, os, json, subprocess

    start_time = time.time()
    try:
        # Huấn luyện bằng subprocess
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        script_path = os.path.join(project_root, 'train_intent.py')

        python_path = sys.executable  
        log_file_path = os.path.join(project_root, "logs/train_output.log")
        with open(log_file_path, "w") as log_file:
            result = subprocess.run(
                [python_path, script_path],
                stdout=log_file,
                stderr=log_file,
                check=True,
                text=True
            )
        
        end_time = time.time()
        actual_time = round(end_time - start_time, 2)

        # Ghi log thời gian huấn luyện
        log_file = "logs/train_logs.json"
        os.makedirs("logs", exist_ok=True)

        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)

        logs.append({
            "timestamp": int(time.time()),
            "duration": actual_time
        })

        # Lưu tối đa 10 bản ghi gần nhất
        with open(log_file, "w") as f:
            json.dump(logs[-10:], f, indent=2)

        return jsonify({
            "success": True,
            "message": "✅ Huấn luyện thành công!",
            "actual_time": actual_time
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
             "message": f"❌ Huấn luyện thất bại! Xem chi tiết log tại logs/train_output.log"
        }), 500

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