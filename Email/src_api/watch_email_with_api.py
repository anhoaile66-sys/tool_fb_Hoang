import time
import os
import json
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from filelock import FileLock
from flask import Flask, request, jsonify
from classSend import run_sent
from classHtmlRender import run_simulator

# --- Cấu hình biến mặc định ---
DEFAULT_CONFIG = {
    "EMP_ID": 22616467,
    "SUBJECT": "",
    "CONTENT": "",
    "MODE": 1
}

# Biến toàn cục để lưu config hiện tại
current_config = DEFAULT_CONFIG.copy()
config_lock = threading.Lock()

# ----------------------------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSINESS_SUBJECT_PATH = os.path.join(BASE_DIR, "..", "business", "business_subject_sample.txt")
BUSINESS_WRITEN_MAIL_PATH = os.path.join(BASE_DIR, "..", "business", "business_writen_mail_sample.txt")

JSON_FILE = os.path.join(BASE_DIR, "..", "business", "business_info.json")
LOCK_FILE = JSON_FILE + ".lock"
EMAIL_LST_FILE = os.path.join(BASE_DIR, "..", "business", "email_lst.json")

# --- Debounce ---
last_trigger = 0
DEBOUNCE_SEC = 2

# --- Flask app cho API ---
app = Flask(__name__)

@app.route('/update-watcher-config', methods=['POST'])
def update_config():
    """API để cập nhật config từ file 1"""
    global current_config
    
    # Ưu tiên lấy từ JSON, nếu không có thì lấy từ form-data
    data = request.get_json(silent=True)
    if not data:
        data = {}
    
    # Lấy dữ liệu từ form nếu không có trong JSON
    for key in ["EMP_ID", "SUBJECT", "CONTENT", "MODE"]:
        key_lower = key.lower()
        if key not in data:
            if key in request.form:
                data[key] = request.form[key]
            elif key_lower in request.form:
                data[key] = request.form[key_lower]
    
    # Kiểm tra có dữ liệu không
    if not data:
        return jsonify({"error": "Không có dữ liệu JSON hoặc form-data"}), 400
    
    with config_lock:
        # Cập nhật các trường có trong request
        for key in ["EMP_ID", "SUBJECT", "CONTENT", "MODE"]:
            key_lower = key.lower()
            if key in data:
                # Convert EMP_ID và MODE về int nếu cần
                if key in ["EMP_ID", "MODE"]:
                    try:
                        current_config[key] = int(data[key])
                    except (ValueError, TypeError):
                        return jsonify({"error": f"Giá trị {key} phải là số"}), 400
                else:
                    current_config[key] = str(data[key])
            elif key_lower in data:
                # Convert EMP_ID và MODE về int nếu cần
                if key in ["EMP_ID", "MODE"]:
                    try:
                        current_config[key] = int(data[key_lower])
                    except (ValueError, TypeError):
                        return jsonify({"error": f"Giá trị {key_lower} phải là số"}), 400
                else:
                    current_config[key] = str(data[key_lower])
    
    print(f"🔄 Config đã được cập nhật: {current_config}")
    return jsonify({
        "status": "updated",
        "config": current_config
    })

@app.route('/get-watcher-config', methods=['GET'])
def get_config():
    """API để xem config hiện tại"""
    with config_lock:
        return jsonify(current_config)

# --- Handler khi file JSON thay đổi ---
class JsonChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_trigger
        if not (event.src_path.endswith("business_info.json") or event.src_path.endswith("email_lst.json")):
            return

        now = time.time()
        if now - last_trigger < DEBOUNCE_SEC:
            return
        last_trigger = now

        try:
            with config_lock:
                config = current_config.copy()
            
            emp_id = config["EMP_ID"]
            subject = config["SUBJECT"]
            content = config["CONTENT"]
            mode = config["MODE"]
            
            with FileLock(LOCK_FILE, timeout=10):
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                emp_id_str = str(emp_id)
                customers = data.get(emp_id_str, {}).get("customers", [])
                has_pending = any(not c.get("sent", False) for c in customers)

            if has_pending:
                print(f"🔔 Có khách hàng mới cho EMP_ID {emp_id}, chạy gửi mail...")
                simulator = run_simulator(emp_id, BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH, MODE=mode)
                simulator.set_subject(subject)
                simulator.set_content(content)
                simulator.beautify_html()
                updated_subject = simulator.get_subject()
                run_sent(emp_id, updated_subject)
            else:
                print("ℹ️ Chưa có khách hàng mới, đợi update tiếp.")
        except Exception as e:
            print(f"⚠️ Lỗi khi đọc JSON hoặc gửi mail: {e}")

def run_flask_app():
    """Chạy Flask app trong thread riêng"""
    app.run(host="0.0.0.0", port=5469, debug=False, use_reloader=False)

def run_file_watcher():
    """Chạy file watcher"""
    event_handler = JsonChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, BASE_DIR, recursive=False)
    observer.start()
    print(f"👂 Đang lắng nghe thay đổi {JSON_FILE} và {EMAIL_LST_FILE} ...")
    
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# --- Khởi động cả Flask và Watcher ---
if __name__ == "__main__":
    print("🚀 Khởi động Watch Email Service...")
    print(f"📡 API Server: http://localhost:5469")
    print(f"🔧 Config mặc định: {current_config}")
    
    # Chạy Flask trong thread riêng
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Chạy file watcher trong main thread
    run_file_watcher()
