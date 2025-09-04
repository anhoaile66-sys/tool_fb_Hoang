import requests
from filelock import FileLock
import json
import os

JSON_FILE = "business_info.json"
LOCK_FILE = JSON_FILE + ".lock"
API_URL = "https://api.timviec365.vn/api/crm/customer/getNTDByEmpIdToGetPhoneNumber"
API_KEY = "1697a131cb22ea0ab9510d379a8151f1"

def load_data():
    with FileLock(LOCK_FILE, timeout=10):
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

def save_data(data):
    with FileLock(LOCK_FILE, timeout=10):
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def append_email(emp_id: int, email: str):
    """Thêm email vào JSON cho đúng nhân viên (nếu chưa có)"""
    data = load_data()
    emp_id_str = str(emp_id)

    if emp_id_str not in data:
        print(f"⚠️ Nhân viên {emp_id} chưa có trong {JSON_FILE}")
        return

    # Nếu chưa có trường customers thì tạo mới
    if "customers" not in data[emp_id_str]:
        data[emp_id_str]["customers"] = []

    # Check trùng
    exists = any(c["email"] == email for c in data[emp_id_str]["customers"])
    if not exists:
        data[emp_id_str]["customers"].append({
            "email": email,
            "sent": False
        })
        print(f"✅ Thêm email {email} cho emp_id {emp_id}")
    else:
        print(f"ℹ️ Email {email} đã tồn tại cho emp_id {emp_id}")

    save_data(data)

def fetch_emails_from_api(emp_ids, size=1):
    """Gọi API lấy email theo danh sách emp_ids"""
    payload = {
        "emp_ids": emp_ids,
        "size": size,
        "key": API_KEY,
        "isGetEmail": True
    }
    headers = {"Content-Type": "application/json"}

    resp = requests.post(API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    data_api = resp.json()

    if not data_api or "data" not in data_api:
        print("⚠️ API không trả về dữ liệu hợp lệ")
        return

    for emp_id in emp_ids:
        emp_id_str = str(emp_id)
        customers = data_api["data"].get(emp_id_str, [])
        for customer in customers:
            email = customer.get("email")
            if email:
                append_email(emp_id, email)

if __name__ == "__main__":
    # ví dụ: đồng bộ email cho Ngô Dung
    fetch_emails_from_api([22615833])
