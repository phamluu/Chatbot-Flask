from flask import Blueprint, Flask, abort, render_template, request, jsonify
import json
from datetime import datetime


test_bp = Blueprint('test_bp', __name__)

@test_bp.get("/test/<page>")
def test_page(page):
    allowed_pages = ["page1", "page2", "page3"]
    if page not in allowed_pages:
        abort(404)
    return render_template(f"test/{page}.html")