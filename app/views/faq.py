# app/views/faq.py
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app import db
from app.models import Faq


faq_bp = Blueprint('faq', __name__)

@faq_bp.route('/faq', methods=['GET'])
def manage_faq():
    faqs = Faq.query.all()
    return render_template('faq.html', faqs=faqs)

@faq_bp.route('/post-faq', methods=['POST'])
def post_faq():
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

# Update FAQ
@faq_bp.route('/faq/update/<int:id>', methods=['POST'])
def update_faq(id):
    faq = Faq.query.get_or_404(id)
    faq.question = request.form.get('question')
    faq.answer = request.form.get('answer')
    db.session.commit()
    flash('FAQ updated successfully!', 'success')
    return redirect(url_for('faq.manage_faq'))

# Delete FAQ
@faq_bp.route('/faq/delete/<int:id>', methods=['POST'])
def delete_faq(id):
    faq = Faq.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted successfully!', 'success')
    return redirect(url_for('faq.manage_faq'))
