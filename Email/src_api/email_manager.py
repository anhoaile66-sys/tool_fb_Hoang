import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "business", "businesses.db")

MAX_PER_DAY = 3
ENABLE_RESET = False  # <-- bật True để auto reset mỗi ngày, False để test

class EmailManager:
    def __init__(self, emp_id: int):
        self.emp_id = str(emp_id)
        self.today = datetime.now().strftime("%Y-%m-%d")
        if ENABLE_RESET:
            self._ensure_reset_today()

    def _get_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_reset_today(self):
        """Reset toàn bộ counters nếu chưa reset hôm nay."""
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Check last reset date (this would require a separate table or a field in email_accounts)
        # For simplicity, let's assume a daily reset mechanism is handled externally or by checking a global setting.
        # A more robust solution would involve a 'last_reset_date' column in email_accounts or a separate 'settings' table.
        
        # For now, we'll just reset if ENABLE_RESET is True and assume it's called once a day.
        # A better approach would be to store the last reset date in the DB.
        
        # Example of a simple reset (without checking last_reset_date in DB for now)
        cursor.execute("UPDATE email_accounts SET num_sent = 0 WHERE emp_id = ?", (self.emp_id,))
        conn.commit()
        conn.close()
        print(f"🔄 Reset toàn bộ counter về 0 cho EMP_ID {self.emp_id} cho ngày {self.today}")


    def get_available_account(self):
        """Trả về email có num_sent < MAX_PER_DAY hoặc None nếu hết."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email_account, id FROM email_accounts WHERE emp_id = ? AND is_active = 1 AND num_sent < ? ORDER BY num_sent ASC LIMIT 1",
            (self.emp_id, MAX_PER_DAY)
        )
        account = cursor.fetchone()
        conn.close()
        if account:
            return account["email_account"]
        return None

    def increase_counter(self, email_account):
        """Tăng counter cho một account trong DB."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE email_accounts SET num_sent = num_sent + 1 WHERE emp_id = ? AND email_account = ?",
            (self.emp_id, email_account)
        )
        conn.commit()
        
        cursor.execute(
            "SELECT num_sent FROM email_accounts WHERE emp_id = ? AND email_account = ?",
            (self.emp_id, email_account)
        )
        new_val = cursor.fetchone()["num_sent"]
        conn.close()
        print(f"🔒 Đã tăng counter {email_account} = {new_val} trong {DB_PATH}")
