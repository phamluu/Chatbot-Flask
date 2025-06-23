# app/views/user.py
from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_socketio import emit
from app import db
from app.models import User

user_bp = Blueprint('user', __name__)


@user_bp.route('/user', methods=['GET', 'POST'])
def manage_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        user_type = request.form.get('user_type')
        if username and email:
            user = User(username=username, email=email, user_type = user_type)
            db.session.add(user)
            db.session.commit()
            flash('user added successfully!', 'success')
        else:
            flash('Please fill in both fields.', 'danger')
        return redirect(url_for('user.manage_user'))

    users = User.query.all()
    return render_template('user.html', users=users)

# Update ChatbotResponse
@user_bp.route('/user/update/<int:id>', methods=['POST'])
def update_chatbot_response(id):
    user = User.query.get_or_404(id)
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.user_type = request.form.get('user_type')
    db.session.commit()
    flash('User Response updated successfully!', 'success')
    return redirect(url_for('user.manage_user'))

# Delete ChatbotResponse
@user_bp.route('/user/delete/<int:id>', methods=['POST'])
def delete_chatbot_response(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User Response deleted successfully!', 'success')
    return redirect(url_for('user.manage_user'))





@user_bp.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@user_bp.route('/chat_post', methods=['POST'])
def chat_post():
    name = request.form['name']
    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()

    users = User.query.all()
    user_data = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
    emit('update_user_list', user_data)

    user_id = new_user.id
    return redirect(url_for('chat.chat', user_id=user_id))