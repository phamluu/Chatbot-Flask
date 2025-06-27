from flask import render_template, redirect, url_for, flash
from app import db
from app.models import User

def handle_manage_user(request):
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        user_type = request.form.get('user_type')

        if username and email:
            user = User(username=username, email=email, user_type=user_type)
            db.session.add(user)
            db.session.commit()
            flash('User added successfully!', 'success')
        else:
            flash('Please fill in all fields.', 'danger')
        return redirect(url_for('user.manage_user'))

    users = User.query.all()
    return render_template('user.html', users=users)

def handle_update_user(id, request):
    user = User.query.get_or_404(id)
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.user_type = request.form.get('user_type')
    db.session.commit()
    flash('User updated successfully!', 'success')
    return redirect(url_for('user.manage_user'))

def handle_delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('user.manage_user'))

def handle_index():
    users = User.query.all()
    return render_template('index.html', users=users)

def handle_chat_post(request):
    name = request.form['name']
    new_user = User(username=name)
    db.session.add(new_user)
    db.session.commit()

    user_id = new_user.id
    return redirect(url_for('chat.chat', user_id=user_id))
