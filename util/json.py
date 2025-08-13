import json

def load_accounts_from_json(file_path):
    """
    Đọc file JSON và trả về danh sách tài khoản (dạng list các dict)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            accounts = json.load(f)
        return accounts
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {e}")
        return []
    
def update_current_account(json_path, device_id, account_name):
    """Cập nhật current_account cho thiết bị trong file JSON"""
    with open(json_path, "r", encoding="utf-8") as f:
        devices = json.load(f)

    for dev in devices:
        if dev["device"] == device_id:
            dev["current_account"] = account_name
            break

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=4, ensure_ascii=False)

    print(f"Đã cập nhật current_account cho {device_id} → {account_name}")