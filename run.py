# run.py
from flask import render_template
from app import create_app, socketio
import sys
sys.stdout.reconfigure(encoding='utf-8')
# import importlib
# importlib.reload(sys)

app = create_app(use_socketio=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
   