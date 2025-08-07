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