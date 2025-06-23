# run.py
from app import app, socketio
import sys
import importlib
importlib.reload(sys)


if __name__ == "__main__":
     socketio.run(app, debug=True)
     