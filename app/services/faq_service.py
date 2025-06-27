from flask import render_template, redirect, url_for, flash
from app import db
from app.models import Faq

def render_faq_list():
    faqs = Faq.query.all()
    return render_template('faq.html', faqs=faqs)

def handle_post_faq(request):
    question = request.form.get('question')
    answer = request.form.get('answer')
    if question and answer:
        new_faq = Faq(question=question, answer=answer)
        db.session.add(new_faq)
        db.session.commit()
        flash('FAQ added successfully!', 'success')
    else:
        flash('Please fill in both fields.', 'danger')
    return redirect(url_for('faq.manage_faq'))

def handle_update_faq(id, request):
    faq = Faq.query.get_or_404(id)
    faq.question = request.form.get('question')
    faq.answer = request.form.get('answer')
    db.session.commit()
    flash('FAQ updated successfully!', 'success')
    return redirect(url_for('faq.manage_faq'))

def handle_delete_faq(id):
    faq = Faq.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted successfully!', 'success')
    return redirect(url_for('faq.manage_faq'))
