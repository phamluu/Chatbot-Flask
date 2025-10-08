# run.py
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import eventlet
eventlet.monkey_patch()  # Sử dụng eventlet để hỗ trợ socketio
from flask import render_template
from app import create_app, socketio
import sys
sys.stdout.reconfigure(encoding='utf-8')
# import importlib
# importlib.reload(sys)

app = create_app(use_socketio=True)

if __name__ == "__main__":
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        debug=True,
        use_reloader=True  # Tắt reloader để tránh lỗi khi sử dụng socketio
    )