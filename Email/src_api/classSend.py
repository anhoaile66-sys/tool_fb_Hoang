import uiautomator2 as u2
import time
import json
import os
from filelock import FileLock
from email_manager import EmailManager

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSINESS_FILE = os.path.join(BASE_DIR, "..", "business", "business_info.json")


class EmailSender:
    def __init__(self, emp_id: int, json_file: str, subject: str, name_acc:str, name_file_attach:str):
        self.emp_id = str(emp_id)
        self.json_file = json_file
        self.subject = subject
        self.name_acc = name_acc
        self.name_file_attach = name_file_attach

        # Load dữ liệu
        with open(self.json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.device_id = self.data[self.emp_id]["device"]
        self.d = u2.connect(self.device_id)
        self.width, self.height = self.d.window_size()
        
    def get_next_customer(self):
        """Lấy email đầu tiên có sent = False"""
        for customer in self.data[self.emp_id]["customers"]:
            if not customer["sent"]:
                return customer
        return None

    def mark_sent(self, email: str):
        """Đánh dấu customer đã gửi email"""
        # lock theo file JSON
        with FileLock(self.json_file + ".lock"):
            # load lại file để chắc chắn dữ liệu mới nhất
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for customer in data[self.emp_id]["customers"]:
                if customer["email"] == email:
                    customer["sent"] = True
                    break

            # ghi đè
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"🔒 Đã đánh dấu {email} = sent:true trong {self.json_file}")

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

        
    def send_email(self, to_email: str, name_file=None):
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

        self.d(resourceId="com.google.android.gm:id/subject").set_text(self.subject)
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
        # print(f"✅ Đã gửi email tới {to_email}")
        self.mark_sent(to_email)
        
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
        
    def run(self):
        customer = self.get_next_customer()
        self.open_gmail()
        if not customer:
            print("🎉 Không còn khách hàng nào cần gửi")
            return
        email = customer["email"]

        self.send_email(email)

# -------- send all pending while accounts còn quota ----------
def send_all_pending(EMP_ID, SUBJECT,NAME_FILE_ATTACH, BUSINESS_FILE=BUSINESS_FILE ):
    manager = EmailManager(EMP_ID)
    while True:
        name_acc = manager.get_available_account()
        if not name_acc:
            print("⚠️ Không còn tài khoản Gmail nào đủ quota để gửi (hoặc hết quota hôm nay).")
            break

        # tạo sender mới (mỗi lần để load latest business_info.json)
        sender = EmailSender(emp_id=EMP_ID, json_file=BUSINESS_FILE, subject=SUBJECT, name_acc=name_acc,name_file_attach=NAME_FILE_ATTACH)

        customer = sender.get_next_customer()
        if not customer:
            print("🎉 Không còn khách hàng nào cần gửi")
            break

        to_email = customer.get("email")
        try:
            sender.open_gmail()
            sender.send_email(to_email)
            manager.increase_counter(name_acc)
            # tuỳ môi trường, bạn có thể tăng sleep nếu UI cần thời gian stable
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Lỗi khi gửi {to_email} bằng {name_acc}: {e}")
            # dừng hoặc tiếp tục tuỳ nhu cầu; hiện dừng để tránh vòng lặp vô hạn
            break

    print("✔️ Kết thúc vòng gửi (send_all_pending).")

def run_sent(EMP_ID, SUBJECT, NAME_FILE_ATTACH="gia_goi.pdf", BUSINESS_FILE=BUSINESS_FILE):
    send_all_pending(EMP_ID, SUBJECT,NAME_FILE_ATTACH, BUSINESS_FILE=BUSINESS_FILE)
