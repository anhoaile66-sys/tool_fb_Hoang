import json
import os
from datetime import datetime

def load_device_account(device_id, folder="devices"):
    """
    Đọc file JSON của từng thiết bị, trả về dict tài khoản của thiết bị đó.
    """
    file_path = os.path.join(folder, f"device_{device_id}.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            account = json.load(f)
        return account
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return {}

def update_current_account(device_id, account_name, folder="devices"):
    """
    Cập nhật current_account cho thiết bị trong file riêng.
    """
    file_path = os.path.join(folder, f"device_{device_id}.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            device = json.load(f)
        device["current_account"] = account_name
        device["time_logged_in"] = datetime.now().isoformat()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(device, f, indent=4, ensure_ascii=False)
        print(f"Đã cập nhật current_account cho {device_id} → {account_name}")
    except Exception as e:
        print(f"Lỗi khi cập nhật file {file_path}: {e}")