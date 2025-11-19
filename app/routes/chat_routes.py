from flask import Blueprint, current_app, render_template, request, jsonify
import os, json
from datetime import datetime
from app.extensions import csrf
from app.extensions import socketio
from flask_socketio import emit

admin_route = Blueprint("admin_route", __name__)

import requests

def get_client_ip():
    # Cloudflare
    if "CF-Connecting-IP" in request.headers:
        return request.headers["CF-Connecting-IP"]

    # Reverse proxy / Load balancer
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"].split(",")[0].strip()

    return request.remote_addr

def get_geo_from_ip(ip):
    try:
        if ip.startswith("127.") or ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
            return {"country": None, "region": None, "city": None}

        url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,query"
        res = requests.get(url, timeout=2).json()

        if res.get("status") == "success":
            return {
                "country": res.get("country"),
                "region": res.get("regionName"),
                "city": res.get("city"),
            }
    except:
        pass

    return {"country": None, "region": None, "city": None}

def get_log_file():
    log_dir = current_app.instance_path
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "tracking.log")
    if not os.path.exists(log_file):
        open(log_file, "a", encoding="utf-8").close()
    return log_file

@csrf.exempt
@admin_route.route("/track", methods=["POST", "OPTIONS"])
def track():
    # ---- xử lý preflight OPTIONS ----
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
    else:
        data = request.json or {}
        if not data:
            response = jsonify({"status": "no data"}), 400
        else:
            data["time"] = datetime.now().isoformat()
            data["ip"] = get_client_ip()
            # Lấy thông tin vị trí
            location = get_geo_from_ip(data["ip"])
            data["location"] = location
            log_path = get_log_file()
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            response = jsonify({"status": "ok"})

    # ---- Thêm header CORS cho cả POST và OPTIONS ----
    response.headers["Access-Control-Allow-Origin"] = "*"  
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    # socketio.emit("new_tracking_event", data, to=None)
    socketio.start_background_task(lambda: socketio.emit("new_tracking_event", data))
    return response

@admin_route.get("/admin/logs")
def admin_logs():
    log_path = get_log_file()
    with open(log_path, "r", encoding="utf-8") as f:
        logs = [json.loads(line) for line in f if line.strip()]
    
    # Sắp xếp logs theo thời gian giảm dần
    logs.sort(key=lambda x: x.get("time", ""), reverse=True)

    return render_template("admin/logs.html", logs=logs)
