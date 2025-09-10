import uiautomator2 as u2
import time
import os
import sqlite3
from email_manager import EmailManager

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "business", "businesses.db")

class EmailSender:
    def __init__(self, emp_id: int, subject: str, content: str, name_acc: str, name_file_attach: str):
        self.emp_id = str(emp_id)
        self.subject = subject
        self.content = content
        self.name_acc = name_acc
        self.name_file_attach = name_file_attach

        self.device_id = self._get_employee_device(self.emp_id)
        if not self.device_id:
            raise ValueError(f"Không tìm thấy device_id cho EMP_ID: {self.emp_id}")
        
        self.d = u2.connect(self.device_id)
        self.width, self.height = self.d.window_size()
        
    def _get_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_employee_device(self, emp_id):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT device FROM employees WHERE emp_id = ?", (emp_id,))
        result = cursor.fetchone()
        conn.close()
        return result["device"] if result else None

    def open_gmail(self):
        """Mở Gmail trên thiết bị"""
        current_app = self.d.app_current()
        if current_app["package"] == "com.google.android.gm":
            print("✅ Đã ở trong Gmail")
            return

        self.d(resourceId="com.android.systemui:id/center_group").click()
        self.d.swipe_ext("up", scale=0.8)
        time.sleep(1)

        self.d(resourceId="com.gogo.launcher:id/search_container_all_apps").click()
        time.sleep(1)
        self.d.send_keys("Gmail", clear=True)
        time.sleep(1)
        self.d(resourceId="com.gogo.launcher:id/icon").click()
        time.sleep(1)
        print("📩 Đang mở Gmail...")
        
    def choose_account(self, name_acc=None):
        """Chọn tài khoản Gmail nếu có nhiều tài khoản"""
        if name_acc is None:
            name_acc = self.name_acc

        # Nhấp vào avatar để mở menu chọn tài khoản
        self.d(resourceId="com.google.android.gm:id/og_apd_internal_image_view").click()
        time.sleep(1)

        # Kiểm tra xem tài khoản đang dùng có phải là name_acc không
        try:
            current_acc = self.d(resourceId="com.google.android.gm:id/og_bento_single_pane_account_menu_title_container").get_text()
            if current_acc == name_acc:
                # print(f"✅ Đang sử dụng tài khoản {name_acc}, chỉ đóng menu")
                self.d(resourceId="com.google.android.gm:id/og_bento_toolbar_close_button").click()
                return
        except Exception:
            # Nếu không lấy được text thì bỏ qua
            pass

        # Chọn tài khoản name_acc nếu có
        try:
            self.d(resourceId="com.google.android.gm:id/og_secondary_account_information", text=name_acc).click()
            print(f"📌 Chuyển sang tài khoản {name_acc}")
            return
        except Exception:
            # Nếu không thấy tài khoản, click vào account thứ 2 như dự phòng
            print("Giữ nguyện tài khoản hiện tại")

        time.sleep(1)
        self.d.press("back")  # Đóng menu chọn tài khoản nếu vẫn mở

        
    def send_email(self, to_email: str, subject: str, content: str, name_file=None):
        if name_file is None:
            name_file = self.name_file_attach
        """Soạn & gửi email"""
        self.choose_account(name_acc=self.name_acc)

        self.d(resourceId="com.google.android.gm:id/compose_button").click()
        time.sleep(1)

        receiver = self.d.xpath(
            '//*[@resource-id="com.google.android.gm:id/peoplekit_autocomplete_chip_group"]/android.widget.EditText[1]'
        )
        receiver.set_text(to_email)
        time.sleep(1)

        self.d.xpath(
            '//*[@resource-id="com.google.android.gm:id/peoplekit_listview_flattened_row"]/android.widget.RelativeLayout[2]'
        ).click()
        time.sleep(1)

        self.d(resourceId="com.google.android.gm:id/subject").set_text(subject)
        time.sleep(1)

        x = self.width * 0.492
        y = self.height * 0.372
        self.d.long_click(x, y, duration=1.0)
        # Kiểm tra và click vào tùy chọn "Dán"
        if self.d(text="Dán").exists(timeout=3):
            self.d(text="Dán").click()
            print("Đã dán thành công")
        else:
            print("Không tìm thấy tùy chọn Dán")

        time.sleep(3)
        self.add_file(name_file=name_file)
        self.d(resourceId="com.google.android.gm:id/send").click()
        print(f"✅ Đã gửi email tới {to_email}")
        return True # Indicate success for now
        
    def add_file(self, name_file):
        self.d(resourceId="com.google.android.gm:id/add_attachment").click()
        time.sleep(1)
        self.d.xpath('//android.widget.ListView/android.widget.LinearLayout[3]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]').click()
        time.sleep(3)
        self.d(description="Hiển thị gốc").click()
        time.sleep(1)
        self.d(resourceId="android:id/title", text="Tài liệu").click()
        time.sleep(1)
        self.d(resourceId="com.google.android.documentsui:id/option_menu_search").click()
        time.sleep(1)
        self.d(resourceId="com.google.android.documentsui:id/search_src_text").click()
        time.sleep(1)
        self.d.send_keys(name_file, clear=True)
        time.sleep(1)
        self.d(resourceId="com.google.android.documentsui:id/thumbnail").click()
        # chọn được là sẽ quay lại mail
        time.sleep(2)
        
# -------- send all pending while accounts còn quota ----------
def run_sent(emp_id, subject, content, to_email, sender_email, name_file_attach="gia_goi.pdf"):
    try:
        sender = EmailSender(emp_id=emp_id, subject=subject, content=content, name_acc=sender_email, name_file_attach=name_file_attach)
        sender.open_gmail()
        success = sender.send_email(to_email, subject, content)
        return success
    except Exception as e:
        print(f"⚠️ Lỗi khi gửi email: {e}")
        return False
