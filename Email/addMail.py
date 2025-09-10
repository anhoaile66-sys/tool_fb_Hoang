import requests
from filelock import FileLock
import json, os
from flask import Flask, request, jsonify
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "business_info.json")
LOCK_FILE = JSON_FILE + ".lock"

app = Flask(__name__)

def save_data(data):
    with FileLock(LOCK_FILE, timeout=10):
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def get_today_date():
    """Lấy ngày hiện tại theo định dạng YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def check_email_exists_today(customers, email, today):
    """Kiểm tra xem email đã tồn tại trong ngày hôm nay chưa"""
    for customer in customers:
        if customer["email"] == email and customer.get("date") == today:
            return True
    return False


@app.route('/add-email', methods=['POST'])
def add_email():
    # Ưu tiên lấy từ JSON, nếu không có thì lấy từ form-data
    data = request.get_json(silent=True)
    if data and "email" in data:
        email = data["email"]
    elif "email" in request.form:
        email = request.form["email"]
    else:
        return jsonify({"error": "Thiếu biến 'email'"}), 400
        
    if data and "emp_id" in data:
        emp_id = data["emp_id"]
        emp_id_str = str(emp_id)
    elif "emp_id" in request.form:
        emp_id = request.form["emp_id"]
        emp_id_str = str(emp_id)
    else:
        return jsonify({"error": "Thiếu biến 'emp_id'"}), 400
    
    # Tạo file JSON nếu chưa tồn tại
    if not os.path.exists(JSON_FILE):
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
    
    today = get_today_date()
    
    with FileLock(LOCK_FILE, timeout=10):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            mail_data = json.load(f)
        
        # Tạo emp_id mới nếu chưa tồn tại
        if emp_id_str not in mail_data:
            mail_data[emp_id_str] = {
                "name": "",
                "device": "",
                "customers": []
            }
        
        # Kiểm tra email đã tồn tại trong ngày hôm nay chưa
        customers = mail_data[emp_id_str]["customers"]
        
        if check_email_exists_today(customers, email, today):
            print(f"ℹ️ Email {email} đã tồn tại cho emp_id {emp_id} trong ngày {today}")
            return jsonify({
                "status": "existed_today", 
                "message": f"Email {email} đã được thêm cho emp_id {emp_id} trong ngày hôm nay",
                "emp_id": emp_id, 
                "email": email,
                "date": today
            })
        
        # Thêm email mới với ngày hiện tại
        new_customer = {
            "email": email,
            "sent": False,
            "date": today
        }
        
        mail_data[emp_id_str]["customers"].append(new_customer)
        print(f"✅ Thêm email {email} cho emp_id {emp_id} vào ngày {today}")
    
    save_data(mail_data)
    return jsonify({
        "status": "added", 
        "emp_id": emp_id, 
        "email": email,
        "date": today
    })


@app.route('/get-emails/<emp_id>', methods=['GET'])
def get_emails(emp_id):
    """API để xem danh sách email của một emp_id"""
    emp_id_str = str(emp_id)
    
    if not os.path.exists(JSON_FILE):
        return jsonify({"error": "Không tìm thấy dữ liệu"}), 404
    
    with FileLock(LOCK_FILE, timeout=10):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            mail_data = json.load(f)
    
    if emp_id_str not in mail_data:
        return jsonify({"error": f"Không tìm thấy emp_id {emp_id}"}), 404
    
    return jsonify({
        "emp_id": emp_id,
        "data": mail_data[emp_id_str]
    })


@app.route('/get-today-emails/<emp_id>', methods=['GET'])
def get_today_emails(emp_id):
    """API để xem danh sách email được thêm hôm nay của một emp_id"""
    emp_id_str = str(emp_id)
    today = get_today_date()
    
    if not os.path.exists(JSON_FILE):
        return jsonify({"error": "Không tìm thấy dữ liệu"}), 404
    
    with FileLock(LOCK_FILE, timeout=10):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            mail_data = json.load(f)
    
    if emp_id_str not in mail_data:
        return jsonify({"error": f"Không tìm thấy emp_id {emp_id}"}), 404
    
    # Lọc các email được thêm hôm nay
    today_emails = [
        customer for customer in mail_data[emp_id_str]["customers"]
        if customer.get("date") == today
    ]
    
    return jsonify({
        "emp_id": emp_id,
        "date": today,
        "today_emails": today_emails,
        "count": len(today_emails)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5468, debug=True)