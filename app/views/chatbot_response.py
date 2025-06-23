# app/views/chatbot_response.py
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app import db
from app.models import ChatbotResponse

chatbot_bp = Blueprint('chatbot_response', __name__)

@chatbot_bp.route('/chatbot-response', methods=['GET'])
def manage_chatbot_response():
    responses = ChatbotResponse.query.all()
    return render_template('chatbot_response.html', responses=responses)

@chatbot_bp.route('/post-chatbot-response', methods=['POST'])
def post_chatbot_response():
        keyword = request.form.get('keyword')
        response = request.form.get('response')
        if keyword and response:
            new_response = ChatbotResponse(keyword=keyword, response=response)
            db.session.add(new_response)
            db.session.commit()
            flash('Chatbot Response added successfully!', 'success')
        else:
            flash('Please fill in both fields.', 'danger')
        return redirect(url_for('chatbot_response.manage_chatbot_response'))



# Update ChatbotResponse
@chatbot_bp.route('/chatbot-response/update/<int:id>', methods=['POST'])
def update_chatbot_response(id):
    response = ChatbotResponse.query.get_or_404(id)
    response.keyword = request.form.get('keyword')
    response.response = request.form.get('response')
    db.session.commit()
    flash('Chatbot Response updated successfully!', 'success')
    return redirect(url_for('chatbot_response.manage_chatbot_response'))

# Delete ChatbotResponse
@chatbot_bp.route('/chatbot-response/delete/<int:id>', methods=['POST'])
def delete_chatbot_response(id):
    response = ChatbotResponse.query.get_or_404(id)
    db.session.delete(response)
    db.session.commit()
    flash('Chatbot Response deleted successfully!', 'success')
    return redirect(url_for('chatbot_response.manage_chatbot_response'))
