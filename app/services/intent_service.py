from datetime import datetime
import json
import os
from flask import render_template, redirect, url_for, flash
from app import db
from app.models import Intent, IntentInput, IntentResponse

# Function to handle intent management
def handle_manage_intent(request):
    if request.method == 'POST':
        intent_code = request.form.get('intent_code')
        intent_name = request.form.get('intent_name')
        description = request.form.get('description')
        if intent_code and intent_name:
            intent = Intent(intent_code=intent_code, intent_name=intent_name, description=description)
            db.session.add(intent)
            db.session.commit()
            flash('Intent added successfully!', 'success')
        else:
            flash('Please fill in all fields.', 'danger')
        return redirect(url_for('intent.manage_intent'))

    intents = Intent.query.all()
     # Đọc thời gian ước tính từ logs
    log_path = "logs/train_logs.json"
    estimated_time = 7.0  # mặc định
    if os.path.exists(log_path):
        with open(log_path) as f:
            logs = json.load(f)
            if logs:
                estimated_time = round(logs[-1]["duration"], 2)
    return render_template('intent.html', intents=intents, estimated_time=estimated_time)

def handle_update_intent(id, request):
    intent = Intent.query.get_or_404(id)
    intent.intent_name = request.form.get('intent_name')
    intent.description = request.form.get('description')
    db.session.commit()
    flash('Intent updated successfully!', 'success')
    return redirect(url_for('intent.manage_intent'))

def handle_delete_intent(id):
    intent = Intent.query.get_or_404(id)
    db.session.delete(intent)
    db.session.commit()
    flash('Intent deleted successfully!', 'success')
    return redirect(url_for('intent.manage_intent'))
#end

# Function to handle intent input management
def handle_manage_intent_input(request, intent_id):
    if request.method == 'POST':
        utterance = request.form.get('utterance')
        if intent_input.utterance:
            intent_input = IntentInput(utterance=utterance, intent_id=intent_id)
            db.session.add(intent_input)
            db.session.commit()
            flash('Câu hỏi cho ý định đã được cập nhật!', 'success')
        else:
            flash('Vui lòng nhập câu hỏi.', 'danger')
        return redirect(url_for('intent.manage_intent_input', intent_id=intent_id))
    intent_inputs = IntentInput.query.filter_by(intent_id=intent_id).all()
    return render_template('intent_input.html', intent_inputs=intent_inputs, intent_id=intent_id)

def handle_update_intent_input(id, request):
    intent_input = IntentInput.query.get_or_404(id)
    intent_input.utterance = request.form.get('utterance')
    db.session.commit()
    flash('Intent updated successfully!', 'success')
    return redirect(url_for('intent.manage_intent_input', intent_id=intent_input.intent_id))

def handle_delete_intent_input(id):
    intent_input = IntentInput.query.get_or_404(id)
    db.session.delete(intent_input)
    db.session.commit()
    flash('Intent deleted successfully!', 'success')
    return redirect(url_for('intent.manage_intent_input', intent_id=intent_input.intent_id))
#end


# Function to handle intent response management
def handle_manage_intent_response(request, intent_id):
    if request.method == 'POST':
        response_text = request.form.get('response_text')
        if response_text:
            intent_response = IntentResponse(response_text=response_text, intent_id=intent_id, created_at=datetime.now())
            db.session.add(intent_response)
            db.session.commit()
            flash('Câu trả lời cho ý định đã được cập nhật!', 'success')
        else:
            flash('Vui lòng nhập câu trả lời.', 'danger')
        return redirect(url_for('intent.manage_intent_responses', intent_id=intent_id))
    intent_responses = IntentResponse.query.filter_by(intent_id=intent_id).order_by(IntentResponse.created_at.desc()).all()
    return render_template('intent_response.html', intent_responses=intent_responses, intent_id=intent_id)

def handle_update_intent_response(id, request):
    intent_response = IntentResponse.query.get_or_404(id)
    intent_response.response_text = request.form.get('response_text')
    db.session.commit()
    flash('Intent updated successfully!', 'success')
    return redirect(url_for('intent.manage_intent_responses', intent_id=intent_response.intent_id))

def handle_delete_intent_response(id):
    intent_response = IntentResponse.query.get_or_404(id)
    db.session.delete(intent_response)
    db.session.commit()
    flash('Intent deleted successfully!', 'success')
    return redirect(url_for('intent.manage_intent_responses', intent_id=intent_response.intent_id))
#end