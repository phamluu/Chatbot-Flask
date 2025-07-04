# run.py
from flask import render_template
from app import create_app, socketio
import sys
import importlib
importlib.reload(sys)

app = create_app()


if __name__ == "__main__":
     socketio.run(app, debug=True)

   