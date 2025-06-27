from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import ChatbotResponse

def render_chatbot_responses():
    responses = ChatbotResponse.query.all()
    return render_template('chatbot_response.html', responses=responses)

def handle_post_response(request):
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

def handle_update_response(id, request):
    response_obj = ChatbotResponse.query.get_or_404(id)
    response_obj.keyword = request.form.get('keyword')
    response_obj.response = request.form.get('response')
    db.session.commit()
    flash('Chatbot Response updated successfully!', 'success')
    return redirect(url_for('chatbot_response.manage_chatbot_response'))

def handle_delete_response(id):
    response_obj = ChatbotResponse.query.get_or_404(id)
    db.session.delete(response_obj)
    db.session.commit()
    flash('Chatbot Response deleted successfully!', 'success')
    return redirect(url_for('chatbot_response.manage_chatbot_response'))
