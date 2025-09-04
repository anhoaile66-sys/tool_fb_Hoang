import requests
from filelock import FileLock
import json, os
from flask import Flask, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "business_info.json")
LOCK_FILE = JSON_FILE + ".lock"
API_URL = "https://api.timviec365.vn/api/crm/customer/getNTDByEmpIdToGetPhoneNumber"
API_KEY = "1697a131cb22ea0ab9510d379a8151f1"

app = Flask(__name__)


def save_data(data):
    with FileLock(LOCK_FILE, timeout=10):
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

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
    
    if not os.path.exists(JSON_FILE):
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
    
    with FileLock(LOCK_FILE, timeout=10):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            mail_data = json.load(f)
            
        # for entry in mail_data:
            # if entry.keys() == emp_id_str:
            #     if entry["status"] == "pending":
            #         return jsonify({"status": "đã tồn tại, chưa đến lượt đăng"})
            #     elif entry["status"] == "posted":
            #         return jsonify({"status": "đã tồn tại, đã đăng"})
            #     elif entry["status"] == "in_progress":
            #         return jsonify({"status": "đã tồn tại, đang xử lý"})


            
        # check trùng        
        exists = any(c["email"] == email for c in mail_data[emp_id_str]["customers"])
        if exists or not exists:
            mail_data[emp_id_str]["customers"].append({
                "email": email,
                "sent": False
            })
            print(f"✅ Thêm email {email} cho emp_id {emp_id}")
        else:
            print(f"ℹ️ Email {email} đã tồn tại cho emp_id {emp_id}")

    save_data(mail_data)
    return jsonify({"status": "added", "emp_id": emp_id, "email": email})


# def fetch_emails_from_api(emp_ids, size=1):
#     """Gọi API lấy email theo danh sách emp_ids"""
#     payload = {
#         "emp_ids": emp_ids,
#         "size": size,
#         "key": API_KEY,
#         "isGetEmail": True
#     }
#     headers = {"Content-Type": "application/json"}

#     resp = requests.post(API_URL, headers=headers, json=payload)
#     resp.raise_for_status()
#     data_api = resp.json()

#     if not data_api or "data" not in data_api:
#         print("⚠️ API không trả về dữ liệu hợp lệ")
#         return

#     for emp_id in emp_ids:
#         emp_id_str = str(emp_id)
#         customers = data_api["data"].get(emp_id_str, [])
#         for customer in customers:
#             email = customer.get("email")
#             if email:
#                 append_email(emp_id, email)

# if __name__ == "__main__":
#     # ví dụ: đồng bộ email cho Ngô Dung
#     fetch_emails_from_api([22615833])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5468, debug=True)