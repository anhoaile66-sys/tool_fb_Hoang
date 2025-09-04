import uiautomator2 as u2
import time
import json
import os
from filelock import FileLock

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LINKS_FILE = os.path.join(BASE_DIR, "business_info.json")

class EmailSender:
    def __init__(self, emp_id: int, json_file: str, subject: str, content: str):
        self.emp_id = str(emp_id)
        self.json_file = json_file
        self.subject = subject
        self.content = content

        # Load dữ liệu
        with open(self.json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.device_id = self.data[self.emp_id]["device"]
        self.d = u2.connect(self.device_id)

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
        time.sleep(2)

        self.d(resourceId="com.gogo.launcher:id/search_container_all_apps").click()
        time.sleep(2)
        self.d.send_keys("Gmail", clear=True)
        time.sleep(2)
        self.d.xpath(
            '//*[@resource-id="com.gogo.launcher:id/branch_suggest_app_list_rv"]/android.view.ViewGroup[1]/android.widget.ImageView[1]'
        ).click()
        time.sleep(3)
        print("📩 Đang mở Gmail...")

    def send_email(self, to_email: str):
        """Soạn & gửi email"""
        self.open_gmail()

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

        self.d(resourceId="com.google.android.gm:id/composearea_tap_trap_bottom").click()
        self.d.send_keys(self.content, clear=True)
        time.sleep(1)

        self.d(resourceId="com.google.android.gm:id/send").click()
        print(f"✅ Đã gửi email tới {to_email}")

    def run(self):
        customer = self.get_next_customer()
        if not customer:
            print("🎉 Không còn khách hàng nào cần gửi")
            return

        email = customer["email"]
        self.send_email(email)
        self.mark_sent(email)


def run_sent(EMP_ID, SUBJECT, CONTENT,LINKS_FILE=LINKS_FILE,BASE_DIR=BASE_DIR):
    sender = EmailSender(EMP_ID, LINKS_FILE, SUBJECT, CONTENT)
    sender.run()
