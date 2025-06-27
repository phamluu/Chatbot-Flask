from flask import Blueprint
from app.services.staff_service import render_staff_page

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff')
def staff():
    return render_staff_page()
