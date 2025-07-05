# wsgi.py
import sys
import os

# Trỏ đến thư mục chứa run.py
sys.path.insert(0, os.path.dirname(__file__))

# Import Flask app từ run.py
from run import app as application
