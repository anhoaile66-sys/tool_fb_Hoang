import uiautomator2 as u2
import time
import random
import os
import json
import io
import base64
import requests
import threading
from threading import Lock
from PIL import Image
from uiautomator2.exceptions import UiObjectNotFoundError
from uiautomator2.exceptions import XPathElementNotFoundError
from uiautomator2 import Direction

# ===== CẤU HÌNH =====
LOG_FILE = "sent_log.txt"
JSON_FILE = "Zalo_data_login_path.json"
API_KEY = "1697a131cb22ea0ab9510d379a8151f1"
API_URL = "https://api.timviec365.vn/api/crm/customer/getNTDByEmpIdToGetPhoneNumber"

# Mapping database ID với tên người gửi
DATABASE_MAPPING = {
    22615833: "Ngô Dung",
    22616467: "Hoàng Linh",
    22636101: "Lê Thùy",
    22789191: "Nhàn",
    22814414: "Bích Ngọc",
    22833463: "Lưu Thư",
    22889226: "Ngọc Hà"
}

DATABASE_IDS = list(DATABASE_MAPPING.keys())

# ===== GIỚI HẠN AN TOÀN =====
MAX_FRIEND_REQUESTS_PER_ACC = 20   # Số lời mời kết bạn tối đa / tài khoản
MAX_NEW_MESSAGES_PER_ACC = 25      # Số tin nhắn tới người lạ tối đa / tài khoản

# Danh sách thiết bị
DEVICE_IDS = ["CEIN4X45I7ZHFEFU", "TSPNH6GYZLPJBY6X", "7DXCUKKB6DVWDAQO"]

# Lock để đồng bộ hóa ghi file
file_lock = Lock()

def random_delay(min_sec=3, max_sec=7):
    delay = random.uniform(min_sec, max_sec)
    print(f"[⏳] Đợi {delay:.2f} giây...")
    time.sleep(delay)

def long_delay():
    delay = random.uniform(600, 900)  # 10-30 phút
    print(f"[🛡️] Nghỉ dài {delay//60:.0f} phút để tránh spam...")
    time.sleep(delay)

def already_sent(phone_number):
    with file_lock:
        if not os.path.exists(LOG_FILE):
            return False
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return phone_number in f.read()

def log_sent(phone_number):
    with file_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(phone_number + "\n")

def get_message_template(sender_name):
    return f"Chào bạn, mình là {sender_name}, nhân viên hỗ trợ bạn của trang web tìm việc 365 ạ, vui lòng kết nối để mình có thể hỗ trợ bạn ạ. Mình cảm ơn!"

def get_phone_numbers_from_api(emp_id, size=1):
    """Lấy danh sách số điện thoại từ API"""
    payload = {
        "emp_ids": [emp_id],
        "size": size,
        "key": API_KEY
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("error") is not None:
            print(f"[❌] Lỗi API: {data.get('error')}")
            return []
        grouped_data = data.get("data", {}).get("grouped", {})
        if str(emp_id) not in grouped_data:
            print(f"[⚠️] Không có dữ liệu cho emp_id {emp_id}")
            return []
        return grouped_data[str(emp_id)]
    except Exception as e:
        print(f"[❌] Lỗi khi gọi API: {e}")
        return []

class DeviceHandler:
    def __init__(self, driver, device_id):
        self.device_id = device_id
        self.d = driver
        self.friend_requests_count = 0
        self.new_messages_count = 0
        self.current_account_index = 0
        self.accounts = []  # Sẽ được khởi tạo khi kết nối
        
    def connect(self):
        try:
            print(f"[✅] Kết nối thiết bị {self.device_id} thành công!")
            self.d.press("home")
            time.sleep(1)
            self.cleanup_background_apps()
            return True
        except Exception as e:
            print(f"[❌] Không thể kết nối với thiết bị {self.device_id}. Lỗi: {e}")
            return False
    
    def cleanup_background_apps(self):
        try:
            self.d(resourceId="com.android.systemui:id/recent_apps").click()
            time.sleep(1)
            if self.d(resourceId="com.gogo.launcher:id/clear_all_button").exists:
                self.d(resourceId="com.gogo.launcher:id/clear_all_button").click()
            else:
                self.d.press("home")
            time.sleep(1)
        except Exception as e:
            print(f"[⚠️] Lỗi khi dọn app chạy ngầm: {e}")
            self.d.press("home")
    
    def switch_account(self):
        try:
            print(f"[{self.device_id}][🔄] Đang chuyển tài khoản...")

            self.d.press("back")
            self.d.press("back")
            self.d.app_start("com.zing.zalo", stop=True)
            random_delay(3, 5)

            # Vào tab cá nhân
            if self.d(description="Cá nhân").exists:
                self.d(description="Cá nhân").click()
                random_delay(2, 3)

            # Vào phần đổi tài khoản
            if self.d(resourceId="com.zing.zalo:id/btn_switch_account").exists:
                self.d(resourceId="com.zing.zalo:id/btn_switch_account").click()
                random_delay(2, 3)

            # Chọn tài khoản kế tiếp
            self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
            acc = self.accounts[self.current_account_index]
            if self.d(text=acc["username"]).exists:
                self.d(text=acc["username"]).click()
                random_delay(3, 5)

            # ✅ Sau khi chọn acc, nếu có nút HOÀN TẤT thì bấm
            if self.d(resourceId="com.zing.zalo:id/btn_chat_gallery_done").exists:
                random_delay(3, 5)
                self.d(resourceId="com.zing.zalo:id/btn_chat_gallery_done").click()
                random_delay(2, 4)

            print(f"[{self.device_id}][✔] Đã chuyển sang tài khoản: {acc['username']}")
            self.friend_requests_count = 0
            self.new_messages_count = 0

        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi khi chuyển tài khoản: {e}")
            self.d.press("home")
            time.sleep(2)

    def change_contact_name(self, phone_number, contact_info):
        """Đổi tên gợi nhớ cho số điện thoại"""
        try:
            cv_title = contact_info.get("cv_title", "").strip()
            name = contact_info.get("name", "").strip()
            new_name = f"{cv_title if cv_title else ' '} {name if name else ' '}".strip()

            print(f"[{self.device_id}][✏️] Đang đổi tên {phone_number} thành '{new_name}'")
            self.d.app_start("com.zing.zalo", stop=True)
            random_delay(3, 5)

            self.d(text="Tìm kiếm").click()
            random_delay()
            self.d(resourceId="com.zing.zalo:id/global_search_edt").click()
            self.d.send_keys(phone_number, clear=True)
            random_delay(2, 3)

            if not self.d(resourceId="com.zing.zalo:id/btn_search_result").exists:
                print(f"[{self.device_id}][⚠️] Không tìm thấy {phone_number} để đổi tên")
                self.d.press("back")
                return False

            self.d(resourceId="com.zing.zalo:id/btn_search_result").click()
            random_delay(2, 4)

            self.d.xpath('//*[@resource-id="com.zing.zalo:id/zalo_action_bar"]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]').click()
            random_delay()

            self.d.xpath('//*[@resource-id="com.zing.zalo:id/user_info_list_view"]/android.widget.RelativeLayout[2]').click()
            random_delay()

            if self.d(resourceId="com.zing.zalo:id/btn_remove_alias").exists:
                self.d(resourceId="com.zing.zalo:id/btn_remove_alias").click()
                random_delay()

            self.d.send_keys(new_name, clear=True)
            random_delay()
            self.d(resourceId="com.zing.zalo:id/btn_save").click()
            random_delay()

            for _ in range(4):
                self.d.press("back")
                random_delay(1, 2)

            print(f"[{self.device_id}][✅] Đã đổi tên {phone_number} thành công")
            return True

        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi khi đổi tên {phone_number}: {e}")
            self.d.press("home")
            return False

    def handle_phone_number(self, phone_number, name=None, sender_name=None):
        """Xử lý gửi tin nhắn và kết bạn cho một số điện thoại. Trả về True nếu đã thao tác được với user."""
        try:
            self.d.app_start("com.zing.zalo", stop=True)
            random_delay(3, 5)
            # ✅ Chỉ đổi tài khoản khi đạt giới hạn
            if (self.friend_requests_count >= MAX_FRIEND_REQUESTS_PER_ACC or 
                self.new_messages_count >= MAX_NEW_MESSAGES_PER_ACC):
                print(f"[{self.device_id}][⚠️] Đạt giới hạn ({self.friend_requests_count} KB / {self.new_messages_count} TN). Chuyển tài khoản...")
                self.switch_account()

            self.d(text="Tìm kiếm").click()
            random_delay()

            self.d.send_keys(phone_number, clear=True)
            random_delay(2, 3)

            if not self.d(resourceId="com.zing.zalo:id/btn_search_result").exists:
                print(f"[{self.device_id}][⚠️] Không tìm thấy kết quả cho {phone_number}, bỏ qua.")
                self.d.press("back")
                return False 

            self.d(resourceId="com.zing.zalo:id/btn_search_result").click()
            random_delay(2, 4)

            message = get_message_template(sender_name)

            # Kịch bản 1: Đã là bạn bè
            if self.d(resourceId="com.zing.zalo:id/chatinput_text").exists:
                print(f"[{self.device_id}][✔] {phone_number} -> Đã là bạn bè. Gửi tin nhắn.")
                self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                self.d.send_keys(message, clear=True)
                random_delay(1,2)
                if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                    self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                self.new_messages_count += 1

            # Kịch bản 2: Đã gửi lời mời
            elif self.d(text="Hủy kết bạn").exists:
                print(f"[{self.device_id}][=] {phone_number} -> Đã gửi lời mời. Gửi thêm tin nhắn.")
                if self.d(resourceId="com.zing.zalo:id/btn_send_message").exists:
                    self.d(resourceId="com.zing.zalo:id/btn_send_message").click()
                    random_delay()
                    self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                    self.d.send_keys(message, clear=True)
                    random_delay(1,2)
                    if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                        self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                    self.new_messages_count += 1
                # long_delay()

            # Kịch bản 3: Chưa kết bạn
            else:
                print(f"[{self.device_id}][!] {phone_number} -> Xử lý như chưa kết bạn.")
                # Thử gửi tin nhắn trước
                if self.d(resourceId="com.zing.zalo:id/btn_send_message").exists:
                    self.d(resourceId="com.zing.zalo:id/btn_send_message").click()
                    random_delay()
                    if self.d(resourceId="com.zing.zalo:id/chatinput_text").exists:
                        self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                        self.d.send_keys(message, clear=True)
                        random_delay(1,2)
                        if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                            self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                            self.new_messages_count += 1
                    random_delay()
                # Thử gửi lời mời kết bạn
                if self.d(resourceId="com.zing.zalo:id/tv_function_privacy").exists:
                    self.d(resourceId="com.zing.zalo:id/tv_function_privacy").click()
                    random_delay()

                sent_request = False
                if self.d(resourceId="com.zing.zalo:id/btnSendInvitation").exists:
                    self.d(resourceId="com.zing.zalo:id/btnSendInvitation").click()
                    self.friend_requests_count += 1
                    sent_request = True
                elif self.d(resourceId="com.zing.zalo:id/btnAddFriend").exists:
                    self.d(resourceId="com.zing.zalo:id/btnAddFriend").click()
                    self.friend_requests_count += 1
                    sent_request = True
                elif self.d(text="GỬI YÊU CẦU").exists:
                    self.d(text="GỬI YÊU CẦU").click()
                    self.friend_requests_count += 1
                    sent_request = True

                if sent_request:
                    print(f"[{self.device_id}][✓] Đã gửi lời mời kết bạn tới {phone_number}")
                else:
                    print(f"[{self.device_id}][⚠] Không tìm thấy nút gửi lời mời cho {phone_number}")

                # long_delay()


            # Quay về màn hình chính
            self.d.press("back")
            random_delay()
            self.d.press("back")
            random_delay()
            return True

        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi khi xử lý {phone_number}: {e}")
            self.d.press("home")
            time.sleep(2)
            return False

    def extract_profile_info(self, phone_number, original_info):
        """Trích xuất thông tin profile Zalo và kết hợp với dữ liệu gốc"""
        print(f"\n[{self.device_id}][*] Bắt đầu trích xuất thông tin cho {phone_number}...")
        try:
            profile_data = {
                "_id": original_info.get("_id", ""),
                "phone": phone_number,
                "name": original_info.get("name", ""),
                "emp_id": original_info.get("emp_id", ""),
                "updated_at": original_info.get("updated_at", ""),
                "cv_title": original_info.get("cv_title", "")
            }

            self.d.app_start("com.zing.zalo", stop=True)
            random_delay(3, 5)
            self.d(text="Tìm kiếm").click()
            random_delay()
            self.d.send_keys(phone_number, clear=True)
            random_delay(2, 3)

            if not self.d(resourceId="com.zing.zalo:id/btn_search_result").exists:
                print(f"[{self.device_id}][!] Không tìm thấy {phone_number} để trích xuất")
                self.d(resourceId="com.zing.zalo:id/search_src_text").click()
                self.d.clear_text()
                self.d.press("back")
                return profile_data  # vẫn trả core-info để còn lưu

            btn = self.d(resourceId="com.zing.zalo:id/btn_search_result")
            text = btn.get_text()
            lines = text.strip().split("\n")
            zalo_name = lines[0].strip() if lines else " "
            print(f"[{self.device_id}][i] Đã tìm thấy tên trên Zalo: {zalo_name}")
            profile_data["zalo_name"] = zalo_name

            btn.click()
            random_delay(2, 4)

            # Xử lý avatar
            avatar_b64 = None
            if self.d(resourceId="com.zing.zalo:id/rounded_avatar_frame").exists(timeout=5):
                iv = self.d(resourceId="com.zing.zalo:id/rounded_avatar_frame")
                img = iv.screenshot()
                max_w, max_h = 200, 200
                img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", optimize=True, quality=75)
                avatar_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                print(f"[{self.device_id}][i] Đã xử lý và mã hóa avatar thành công.")
            else:
                print(f"[{self.device_id}][!] Không tìm thấy khung avatar cho {zalo_name}")
            profile_data["ava"] = avatar_b64

            self.d.press("back")
            time.sleep(1)

            return profile_data

        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi khi trích xuất thông tin của {phone_number}: {e}")
            self.d.press("home")
            time.sleep(2)
            # vẫn trả dữ liệu cơ bản để không mất lần xử lý này
            return {
                "_id": original_info.get("_id", ""),
                "phone": phone_number,
                "name": original_info.get("name", ""),
                "emp_id": original_info.get("emp_id", ""),
                "updated_at": original_info.get("updated_at", ""),
                "cv_title": original_info.get("cv_title", ""),
                "zalo_name": None,
                "ava": None
            }

    def upsert_profile_json(self, profile):
        """Chèn hoặc cập nhật 1 bản ghi hồ sơ theo phone vào JSON_FILE, thực hiện ngay."""
        try:
            with file_lock:
                try:
                    with open(JSON_FILE, "r", encoding="utf-8") as f:
                        all_profiles = json.load(f)
                    if not isinstance(all_profiles, list):
                        all_profiles = []
                except (FileNotFoundError, json.JSONDecodeError):
                    all_profiles = []

                phone = profile.get("phone")
                found = False
                for i, p in enumerate(all_profiles):
                    if p.get("phone") == phone:
                        all_profiles[i] = profile  # cập nhật
                        found = True
                        break
                if not found:
                    all_profiles.append(profile)

                with open(JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_profiles, f, ensure_ascii=False, indent=4)
                print(f"[{self.device_id}][💾] Đã ghi JSON ngay cho {phone}")
                return True
        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi ghi JSON cho {profile.get('phone')}: {e}")
            return False

    def process_phone_number(self, phone_number, contact_info, sender_name):
        """Xử lý hoàn chỉnh một số điện thoại"""
        if already_sent(phone_number):
            print(f"[{self.device_id}][⏭] Bỏ qua {phone_number} (đã có trong log)")
            return

        try:
            # 1) Nhắn tin/ gửi kết bạn
            interacted = self.handle_phone_number(phone_number, contact_info.get("name", ""), sender_name)

            if not interacted:
                print(f"[{self.device_id}][⚠️] Bỏ qua đổi tên & lưu JSON cho {phone_number} vì không tương tác được")
                random_delay(3, 5)
                return

            # 2) Đổi tên gợi nhớ NGAY
            self.change_contact_name(phone_number, contact_info)

            # 3) Trích xuất profile NGAY
            profile_data = self.extract_profile_info(phone_number, contact_info)

            # 4) Ghi JSON NGAY (upsert)
            self.upsert_profile_json(profile_data)

            # 5) Ghi log đã gửi để tránh trùng
            log_sent(phone_number)

        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi tổng khi xử lý {phone_number}: {e}")

        # 6) Nghỉ ngắn trước khi sang số kế tiếp
        random_delay(5, 10)

    def run(self, rounds=2):
        """Chạy chính trên thiết bị này"""
        while rounds > 0:
            current_db = random.choice(DATABASE_IDS)
            sender_name = DATABASE_MAPPING.get(current_db, "Nhân viên")
            print(f"\n[{self.device_id}]===== ĐANG LÀM VIỆC VỚI DATABASE {current_db} - {sender_name} =====")

            phone_data = get_phone_numbers_from_api(current_db)
            if not phone_data:
                print(f"[{self.device_id}][⚠️] Không có dữ liệu từ database {current_db}, chuyển sang database khác")
                continue

            for item in phone_data:
                phone_number = item.get("phone_number", "").strip()
                if not phone_number:
                    continue

                self.process_phone_number(phone_number, item, sender_name)

            print(f"\n[{self.device_id}]🎉 Hoàn tất một vòng xử lý theo cơ chế mới (xử lý từng số ngay).")
            rounds -= 1

def main():
    # Khởi tạo và kết nối các thiết bị
    device_handlers = []
    for device_id in DEVICE_IDS:
        handler = DeviceHandler(device_id)
        if handler.connect():
            device_handlers.append(handler)
    
    if not device_handlers:
        print("❌ Không có thiết bị nào kết nối thành công!")
        return
    
    # Tạo và chạy các luồng
    threads = []
    for handler in device_handlers:
        t = threading.Thread(target=handler.run, args=(2,))  # 2 rounds mỗi thiết bị
        t.start()
        threads.append(t)
    
    # Đợi tất cả các luồng hoàn thành
    for t in threads:
        t.join()
    
    print("\n🎉 Tất cả thiết bị đã hoàn thành công việc!")

if __name__ == "__main__":
    main()