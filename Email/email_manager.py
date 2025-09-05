import os
import json
from filelock import FileLock
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMAIL_LST_FILE = os.path.join(BASE_DIR, "email_lst.json")
LOCK_FILE = EMAIL_LST_FILE + ".lock"

MAX_PER_DAY = 3
ENABLE_RESET = False  # <-- bật True để auto reset mỗi ngày, False để test

class EmailManager:
    def __init__(self, emp_id: int):
        self.emp_id = str(emp_id)
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.reset_happened = False
        if ENABLE_RESET:
            self.reset_happened = self._ensure_reset_today()

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
        """Reset toàn bộ counters nếu chưa reset hôm nay. Trả về True nếu có reset."""
        data = self._load_data()
        last_reset = data.get("__last_reset__")
        if last_reset == self.today:
            return False

        # reset counts
        for emp, accounts in list(data.items()):
            if emp.startswith("__"):
                continue
            for acc in accounts:
                email = list(acc.keys())[0]
                acc[email] = 0

        data["__last_reset__"] = self.today
        self._save_data(data)
        print(f"🔄 Reset toàn bộ counter về 0 cho ngày {self.today}")
        return True

    def get_available_account(self):
        """Trả về email có count < MAX_PER_DAY hoặc None nếu hết."""
        data = self._load_data()
        accounts = data.get(self.emp_id, [])
        for acc in accounts:
            email, count = list(acc.items())[0]
            if count < MAX_PER_DAY:
                return email
        return None

    def increase_counter(self, email):
        """Tăng counter cho một account (với FileLock)."""
        data = self._load_data()
        accounts = data.get(self.emp_id, [])
        for acc in accounts:
            if email in acc:
                acc[email] = acc[email] + 1
                new_val = acc[email]
                break
        else:
            new_val = None

        self._save_data(data)
        print(f"🔒 Đã tăng counter {email} = {new_val} trong {EMAIL_LST_FILE}")
