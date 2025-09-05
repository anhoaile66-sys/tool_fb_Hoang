import os
import json
from filelock import FileLock
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMAIL_LST_FILE = os.path.join(BASE_DIR, "email_lst.json")
LOCK_FILE = EMAIL_LST_FILE + ".lock"

MAX_PER_DAY = 3
ENABLE_RESET = False  # ✅ bật/tắt reset theo ngày

class EmailManager:
    def __init__(self, emp_id: int):
        self.emp_id = str(emp_id)
        self.today = datetime.now().strftime("%Y-%m-%d")
        if ENABLE_RESET:
            self._ensure_reset_today()  # kiểm tra khi khởi tạo

    def _load_data(self):
        with FileLock(LOCK_FILE, timeout=10):
            if not os.path.exists(EMAIL_LST_FILE):
                return {}
            with open(EMAIL_LST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_data(self, data):
        with FileLock(LOCK_FILE, timeout=10):
            with open(EMAIL_LST_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def _ensure_reset_today(self):
        """Kiểm tra nếu sang ngày mới thì reset tất cả counter về 0"""
        data = self._load_data()
        last_reset = data.get("__last_reset__")

        if last_reset != self.today:
            for emp, accounts in data.items():
                if emp.startswith("__"):  # bỏ qua key đặc biệt
                    continue
                for acc in accounts:
                    email = list(acc.keys())[0]
                    acc[email] = 0
            data["__last_reset__"] = self.today
            self._save_data(data)
            print(f"🔄 Reset toàn bộ counter về 0 cho ngày {self.today}")

    def get_available_account(self):
        """Lấy tài khoản Gmail còn quota < MAX_PER_DAY"""
        data = self._load_data()
        accounts = data.get(self.emp_id, [])

        for acc in accounts:
            email, count = list(acc.items())[0]
            if count < MAX_PER_DAY:
                return email
        return None

    def increase_counter(self, email):
        """Tăng counter sau khi gửi thành công"""
        data = self._load_data()
        accounts = data.get(self.emp_id, [])

        for acc in accounts:
            if email in acc:
                acc[email] = acc[email] + 1
                break

        self._save_data(data)
        print(f"🔒 Đã tăng counter {email} = {acc[email]} trong {EMAIL_LST_FILE}")
