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
from queue import Queue, Empty
from collections import defaultdict
from PIL import Image
from uiautomator2.exceptions import UiObjectNotFoundError
from uiautomator2.exceptions import XPathElementNotFoundError
from uiautomator2 import Direction

# ===================== CẤU HÌNH / HẰNG SỐ =====================
USED_ACCOUNTS = {}  # {device_id: [list tên tài khoản đã dùng trong phiên chạy]}
ACCOUNT_CANDIDATES = {}  # {device_id: [list tên tài khoản hiển thị lần gần nhất]}

LOG_FILE = "sent_log.txt"
JSON_FILE = "Zalo_data_login_path.json"
API_KEY = "1697a131cb22ea0ab9510d379a8151f1"
API_URL = "https://api.timviec365.vn/api/crm/customer/getNTDByEmpIdToGetPhoneNumber"

# Mapping database ID -> tên người gửi (KHÔNG ĐỔI)
DATABASE_MAPPING = {
    22615833: "Ngô Dung",
    22616467: "Hoàng Linh",
    22636101: "Lê Thùy",
    22789191: "Nhàn",
    22814414: "Bích Ngọc",
    22833463: "Lưu Thư",
    22889226: "Ngọc Hà",
    22894754: "Hải Yến",
    22889521: "Ngọc Mai"
}
DATABASE_IDS = list(DATABASE_MAPPING.keys())

# ============ THÊM MAPPING THIẾT BỊ -> DATABASE THEO YÊU CẦU ============
# Lưu ý: các device KHÔNG có trong map này sẽ mặc định dùng Ngô Dung (22615833)
DEVICE_TO_DATABASE = {
    # Có sẵn trước đây
    "EQLNQ8O7EQCQPFXG": 22616467,  # Hoàng Linh
    "YH9TSS7XCMPFZHNR": 22616467,  # Hoàng Linh
    "MJZDFY896TMJBUPN": 22616467,  # Hoàng Linh
    "8HMN4T9575HAQWLN": 22894754,  # Hải Yến
    "CQIZKJ8P59AY7DHI": 22889226,  # Ngọc Hà
    "9PAM7DIFW87DOBEU": 22615833,  # Ngô Dung


    "PN59BMHYPFXCPN8T": 22889521,  # Ngọc Mai
    "F6NZ5LRKWWGACYQ8": 22789191,  # Nhàn
    "EM4DYTEITCCYJNFU": 22616467,  # Hoàng Linh
    "QK8TEMKZMBYHPV6P": 22833463,  # Lưu Thư
    "IJP78949G69DKNHM": 22636101,  # Lê Thùy
}

DEFAULT_DB_ID = 22615833  # Mặc định: Ngô Dung

def get_database_for_device(device_id: str) -> int:
    """Trả về database_id ứng với thiết bị; mặc định Ngô Dung nếu không có map."""
    return DEVICE_TO_DATABASE.get(device_id, DEFAULT_DB_ID)

# ===== GIỚI HẠN AN TOÀN =====
MAX_FRIEND_REQUESTS_PER_ACC = 20 # Số lời mời kết bạn tối đa / tài khoản
MAX_NEW_MESSAGES_PER_ACC = 20   # Số tin nhắn tới người lạ tối đa / tài khoản

# Danh sách thiết bị (ĐÃ THÊM 5 THIẾT BỊ MỚI)
DEVICE_IDS = [
    "CEIN4X45I7ZHFEFU",
    "TSPNH6GYZLPJBY6X",
    "7DXCUKKB6DVWDAQO",
    "8HMN4T9575HAQWLN",
    "CQIZKJ8P59AY7DHI",
    "EQLNQ8O7EQCQPFXG",
    "YH9TSS7XCMPFZHNR",
    "9PAM7DIFW87DOBEU",
    "MJZDFY896TMJBUPN",
    "7HYP4T4XTS4DXKCY",
    "UWJJOJLB85SO7LIZ",

    # MỚI THÊM
    "F6NZ5LRKWWGACYQ8",
    "EM4DYTEITCCYJNFU",
    "QK8TEMKZMBYHPV6P",
    "IJP78949G69DKNHM",
    "PN59BMHYPFXCPN8T",
]

# ===== GÁN DATABASE THEO TỪNG THIẾT BỊ (tương tự DEVICE_TO_DATABASE) =====
# Giữ lại để tương thích với code cũ, nhưng có fallback mặc định.
DEVICE_DB_PREF = {
    "EQLNQ8O7EQCQPFXG": 22616467,  # Hoàng Linh
    "YH9TSS7XCMPFZHNR": 22616467,  # Hoàng Linh
    "MJZDFY896TMJBUPN": 22616467,  # Hoàng Linh
    "8HMN4T9575HAQWLN": 22894754,  # Hải Yến
    "CQIZKJ8P59AY7DHI": 22889226,  # Ngọc Hà
    "9PAM7DIFW87DOBEU": 22615833,  # Ngô Dung

    "PN59BMHYPFXCPN8T": 22889521,  # Ngọc Mai
    "F6NZ5LRKWWGACYQ8": 22789191,  # Nhàn
    "EM4DYTEITCCYJNFU": 22616467,  # Hoàng Linh
    "QK8TEMKZMBYHPV6P": 22833463,  # Lưu Thư
    "IJP78949G69DKNHM": 22636101,  # Lê Thùy
}

# ===== BIẾN DÙNG CHUNG TOÀN CHƯƠNG TRÌNH (ĐỒNG BỘ NHIỀU THIẾT BỊ) =====
file_lock = Lock()                     # Khóa ghi file (log, json)
db_lock = Lock()                       # Khóa nạp dữ liệu cho queue theo DB
db_queues = defaultdict(Queue)         # Hàng đợi theo từng emp_id
db_loaded = set()                      # Đánh dấu DB đã nạp
db_enqueued_phones = defaultdict(set)  # Theo dõi những số đã enqueue (tránh trùng)
STOP_EVENT = threading.Event()         # Có thể dùng để dừng khẩn cấp

# ===================== TIỆN ÍCH =====================
def random_delay(min_sec=3, max_sec=7):
    delay = random.uniform(min_sec, max_sec)
    print(f"[⏳] Đợi {delay:.2f} giây...")
    time.sleep(delay)

def long_delay():
    delay = random.uniform(600, 900)  # 10-15 phút
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

# ===================== API LẤY SỐ =====================
def get_phone_numbers_from_api(emp_ids, size=180, get_fb_link=True):
    """Lấy danh sách số điện thoại từ API cho nhiều emp_ids"""
    payload = {
        "emp_ids": emp_ids if isinstance(emp_ids, list) else [emp_ids],
        "size": size,
        "key": API_KEY,
        "getFbLink": get_fb_link
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("error") is not None:
            print(f"[❌] Lỗi API: {data.get('error')}")
            return []

        grouped_data = data.get("data", {})
        results = []
        for eid in payload["emp_ids"]:
            eid_str = str(eid)
            if eid_str in grouped_data:
                results.extend(grouped_data[eid_str])
            else:
                print(f"[⚠️] Không có dữ liệu cho emp_id {eid}")
        return results
    except Exception as e:
        print(f"[❌] Lỗi khi gọi API: {e}")
        return []

def ensure_db_queue_loaded(emp_id, min_batch_size=90):
    """
    Đảm bảo hàng đợi cho emp_id đã được nạp dữ liệu.
    - Chỉ nạp 1 lần (hoặc khi hàng trống) nhờ db_lock.
    - Lọc bỏ số đã gửi (LOG_FILE) và số đã enqueue trước đó (db_enqueued_phones[emp_id]).
    """
    if not db_queues[emp_id].empty():
        return

    with db_lock:
        if not db_queues[emp_id].empty():
            return

        print(f"[DB {emp_id}] 🔄 Nạp dữ liệu vào hàng đợi...")
        data = get_phone_numbers_from_api(emp_id, size=min_batch_size, get_fb_link=True)
        if not data:
            print(f"[DB {emp_id}] ⚠️ Không có dữ liệu để nạp.")
            return

        enq_set = db_enqueued_phones[emp_id]
        added = 0
        for item in data:
            phone = (item.get("phone_number") or "").strip()
            if not phone:
                continue
            if already_sent(phone):
                continue
            if phone in enq_set:
                continue
            db_queues[emp_id].put(item)
            enq_set.add(phone)
            added += 1

        if added > 0:
            print(f"[DB {emp_id}] ✅ Đã nạp {added} mục vào hàng đợi.")
        else:
            print(f"[DB {emp_id}] ⚠️ Không có mục hợp lệ để nạp.")

# ===================== DEVICE HANDLER =====================
class DeviceHandler:
    def __init__(self, driver, device_id):
        self.device_id = device_id
        self.d = driver
        self.friend_requests_count = 0
        self.new_messages_count = 0
        self.current_account_index = 0  # Giữ để tương thích
        self.accounts = []  # Nếu có nhiều tài khoản, hãy điền [{ "username": "..."}]

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

    # ===================== ĐỔI TÀI KHOẢN THEO YÊU CẦU =====================
    def _read_visible_accounts(self):
        """
        Đọc 3 tài khoản hiển thị tại màn hình đổi tài khoản:
        xpath gốc: //*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout[i]/android.widget.TextView[2]
        Trả về list tên theo thứ tự.
        """
        names = []
        try:
            rows = self.d.xpath('//*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout').all()
            for idx in range(1, len(rows) + 1):
                tv2 = self.d.xpath(f'//*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout[{idx}]/android.widget.TextView[2]')
                try:
                    name = tv2.get_text().strip()
                except Exception:
                    name = ""
                if name:
                    names.append(name)
        except Exception as e:
            print(f"[{self.device_id}] [⚠️] Không đọc được danh sách tài khoản: {e}")
        return names

    def switch_account(self):
        """
        Đổi tài khoản Zalo đúng chuỗi bạn yêu cầu:

        1) d(resourceId="com.zing.zalo:id/maintab_metab").click()
        2) d(resourceId="com.zing.zalo:id/avt_right_list_me_tab").click()
        3) d.xpath('//*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout[2]/android.widget.TextView[2]').click()
        (fallback: dùng 'recycler_view' nếu 'recycle_view' không tồn tại)
        4) chờ 10 giây
        5) d(resourceId="com.zing.zalo:id/btn_chat_gallery_done").click() (fallback: bấm theo text 'Hoàn tất')

        Đồng thời: trích và nhớ 3 tên tài khoản đang hiển thị để tránh lặp.
        Sau khi đổi account, reset quota đếm gửi lời mời/tin nhắn.
        """
        device_id = self.device_id
        if device_id not in USED_ACCOUNTS:
            USED_ACCOUNTS[device_id] = []

        def _wait(cond_fn, timeout=10, interval=0.5, desc=""):
            t0 = time.time()
            while time.time() - t0 < timeout:
                try:
                    if cond_fn():
                        return True
                except Exception:
                    pass
                time.sleep(interval)
            if desc:
                print(f"[{device_id}] [⏳→❌] Hết thời gian chờ: {desc}")
            return False

        print(f"[{device_id}] 🔄 Bắt đầu quy trình đổi tài khoản...")

        # B1: mở tab Me
        if not _wait(lambda: self.d(resourceId="com.zing.zalo:id/maintab_metab").exists, 8, 0.4, "tab Me xuất hiện"):
            print(f"[{device_id}] [⚠] Không thấy tab Me. Thử mở app lại.")
            try:
                self.d.app_start("com.zing.zalo")
            except Exception:
                pass
            _wait(lambda: self.d(resourceId="com.zing.zalo:id/maintab_metab").exists, 8, 0.4, "tab Me sau khi mở app")

        try:
            self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
        except Exception as e:
            print(f"[{device_id}] [⚠] Không bấm được tab Me: {e}")

        # B2: bấm avatar (mở danh sách tài khoản)
        if not _wait(lambda: self.d(resourceId="com.zing.zalo:id/avt_right_list_me_tab").exists, 6, 0.3, "avatar xuất hiện"):
            print(f"[{device_id}] [⚠] Không tìm thấy avatar để mở danh sách tài khoản.")
            return False
        try:
            self.d(resourceId="com.zing.zalo:id/avt_right_list_me_tab").click()
        except Exception as e:
            print(f"[{device_id}] [⚠] Click avatar lỗi: {e}")
            return False

        time.sleep(1.2)

        # B3: chờ danh sách tài khoản hiển thị (recycle_view hoặc recycler_view)
        def _accounts_view_exists():
            return (
                self.d.xpath('//*[@resource-id="com.zing.zalo:id/recycle_view"]').exists or
                self.d.xpath('//*[@resource-id="com.zing.zalo:id/recycler_view"]').exists
            )
        if not _wait(_accounts_view_exists, 8, 0.4, "danh sách tài khoản hiện ra"):
            print(f"[{device_id}] [⚠] Không thấy danh sách tài khoản (recycle/recycler_view).")
            return False

        # Trích 3 tên tài khoản để ghi nhớ
        visible_names = []
        try:
            # Ưu tiên recycle_view
            base_id = "recycle_view" if self.d.xpath('//*[@resource-id="com.zing.zalo:id/recycle_view"]').exists else "recycler_view"
            rows = self.d.xpath(f'//*[@resource-id="com.zing.zalo:id/{base_id}"]/android.widget.LinearLayout').all()
            for idx in range(1, min(len(rows), 3) + 1):
                tv2 = self.d.xpath(f'//*[@resource-id="com.zing.zalo:id/{base_id}"]/android.widget.LinearLayout[{idx}]/android.widget.TextView[2]')
                try:
                    nm = tv2.get_text().strip()
                except Exception:
                    nm = ""
                if nm:
                    visible_names.append(nm)
        except Exception as e:
            print(f"[{device_id}] [⚠] Lỗi khi đọc tên tài khoản: {e}")

        ACCOUNT_CANDIDATES.setdefault(device_id, [])
        ACCOUNT_CANDIDATES[device_id] = visible_names[:]
        print(f"[{device_id}] 👥 3 tài khoản hiển thị: {visible_names if visible_names else 'Không đọc được'}")

        # Theo yêu cầu: CLICK CHÍNH XÁC TÀI KHOẢN THỨ 2
        # (Nếu không tồn tại dòng 2, fallback: thử dòng 1 rồi dòng 3)
        clicked = False
        for try_idx in [2, 1, 3]:
            xpath_try = f'//*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout[{try_idx}]/android.widget.TextView[2]'
            xpath_alt = f'//*[@resource-id="com.zing.zalo:id/recycler_view"]/android.widget.LinearLayout[{try_idx}]/android.widget.TextView[2]'
            target_xpath = xpath_try if self.d.xpath('//*[@resource-id="com.zing.zalo:id/recycle_view"]').exists else xpath_alt

            if self.d.xpath(target_xpath).exists:
                try:
                    name_try = ""
                    try:
                        name_try = self.d.xpath(target_xpath).get_text().strip()
                    except Exception:
                        pass
                    print(f"[{device_id}] 👉 Chọn tài khoản dòng {try_idx}{f' ({name_try})' if name_try else ''}")
                    self.d.xpath(target_xpath).click()
                    clicked = True
                    break
                except Exception as e:
                    print(f"[{device_id}] [⚠] Click dòng {try_idx} lỗi: {e}")

        if not clicked:
            print(f"[{device_id}] [❌] Không click được bất kỳ dòng tài khoản nào (1/2/3).")
            return False

        # B4: chờ 10 giây
        print(f"[{device_id}] ⏳ Chờ 10 giây sau khi chọn tài khoản...")
        time.sleep(10)

        # B5: bấm nút Hoàn tất
        done_clicked = False
        try:
            if self.d(resourceId="com.zing.zalo:id/btn_chat_gallery_done").exists:
                self.d(resourceId="com.zing.zalo:id/btn_chat_gallery_done").click()
                done_clicked = True
        except Exception as e:
            print(f"[{device_id}] [⚠] Bấm bằng resourceId nút Hoàn tất lỗi: {e}")

        if not done_clicked:
            # Fallback theo TEXT
            try:
                if self.d(text="Hoàn tất").exists:
                    self.d(text="Hoàn tất").click()
                    done_clicked = True
            except Exception as e:
                print(f"[{device_id}] [⚠] Bấm bằng text 'Hoàn tất' lỗi: {e}")

        if not done_clicked:
            print(f"[{device_id}] [⚠] Không tìm được nút Hoàn tất. Thử nhấn back rồi vào lại tab Me.")
            self.d.press("back")

        # Ghi nhớ: đừng chọn trùng trong lần sau
        try:
            # Nếu đọc được tên đã chọn (ở bước trên)
            chosen_name = None
            try:
                # Ưu tiên lấy theo vị trí dòng 2 nếu có
                if len(ACCOUNT_CANDIDATES.get(device_id, [])) >= 2:
                    chosen_name = ACCOUNT_CANDIDATES[device_id][1]
            except Exception:
                pass
            if chosen_name:
                USED_ACCOUNTS[device_id].append(chosen_name)
        except Exception:
            pass

        # Reset quota vì đã đổi tài khoản
        self.friend_requests_count = 0
        self.new_messages_count = 0

        print(f"[{device_id}] ✅ Hoàn tất đổi tài khoản. Đã reset quota cho tài khoản mới.")
        time.sleep(2)
        return True


    # ===================== NGHIỆP VỤ ZALO =====================
    def change_contact_name(self, phone_number, contact_info):
        """Đổi tên gợi nhớ cho số điện thoại"""
        try:
            cv_title = (contact_info.get("cv_title") or "").strip()
            name = (contact_info.get("name") or "").strip()
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
        """Gửi tin nhắn/kết bạn cho một số điện thoại. Trả True nếu đã thao tác."""
        try:
            self.d.app_start("com.zing.zalo", stop=True)
            random_delay(3, 5)

            # Đổi tài khoản nếu đã đạt giới hạn
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
                random_delay(1, 2)
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
                    random_delay(1, 2)
                    if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                        self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                    self.new_messages_count += 1

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
                        random_delay(1, 2)
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

            # Quay về
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
                return profile_data

            btn = self.d(resourceId="com.zing.zalo:id/btn_search_result")
            try:
                text = btn.get_text()
                lines = text.strip().split("\n")
                zalo_name = lines[0].strip() if lines else " "
            except Exception:
                zalo_name = " "
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

    def pick_database_for_round(self):
        """
        Chọn database cho thiết bị:
        - Nếu có mapping cố định thì dùng luôn.
        - Nếu không, dùng DEFAULT_DB_ID (Ngô Dung).
        """
        preferred_db = DEVICE_DB_PREF.get(self.device_id)
        if preferred_db in DATABASE_MAPPING:
            return preferred_db
        # fallback tuyệt đối theo yêu cầu
        return DEFAULT_DB_ID

    def run(self, rounds=1):
        """Chạy chính trên thiết bị này: LẤY CÔNG VIỆC TỪ HÀNG ĐỢI CHUNG THEO DATABASE"""
        while rounds > 0 and not STOP_EVENT.is_set():
            current_db = self.pick_database_for_round()
            sender_name = DATABASE_MAPPING.get(current_db, "Nhân viên")
            print(f"\n[{self.device_id}]===== LẤY VIỆC TỪ DATABASE {current_db} - {sender_name} =====")

            # Đảm bảo đã có dữ liệu trong hàng đợi của DB này
            ensure_db_queue_loaded(current_db)

            empty_streak = 0

            # Đổi account nếu đạt giới hạn
            if (self.friend_requests_count >= MAX_FRIEND_REQUESTS_PER_ACC or
                self.new_messages_count >= MAX_NEW_MESSAGES_PER_ACC):
                print(f"[{self.device_id}][⚠️] Đạt giới hạn ({self.friend_requests_count} KB / {self.new_messages_count} TN). Chuyển tài khoản...")
                self.switch_account()

            try:
                contact = db_queues[current_db].get(timeout=5)  # chờ 5s nếu tạm thời trống
                phone_number = (contact.get("phone_number") or "").strip()
                if not phone_number:
                    continue
                self.process_phone_number(phone_number, contact, sender_name)
                db_queues[current_db].task_done()
                empty_streak = 0
            except Empty:
                empty_streak += 1
                print(f"[{self.device_id}][{current_db}] ⏳ Hết việc tạm thời (lần {empty_streak}).")
                ensure_db_queue_loaded(current_db)
                if empty_streak >= 3:
                    print(f"[{self.device_id}] 💤 Kết thúc vòng vì DB {current_db} hết việc.")
                    break

            print(f"\n[{self.device_id}]🎉 Hoàn tất một vòng xử lý (hàng đợi chung, không trùng số).")
            rounds -= 1

# ===================== MAIN =====================
def main():
    # Khởi tạo và kết nối các thiết bị
    device_handlers = []
    for device_id in DEVICE_IDS:
        try:
            d = u2.connect(device_id)
        except Exception as e:
            print(f"[❌] Không kết nối được tới {device_id}: {e}")
            continue

        handler = DeviceHandler(d, device_id)
        if handler.connect():
            device_handlers.append(handler)

    if not device_handlers:
        print("❌ Không có thiết bị nào kết nối thành công!")
        return

    # (Tùy chọn) Nạp trước hàng đợi cho các DB được gán cố định để giảm độ trễ ban đầu
    prefetch_dbs = set(DEVICE_DB_PREF.values()) | {DEFAULT_DB_ID}
    for emp_id in prefetch_dbs:
        ensure_db_queue_loaded(emp_id)

    # Tạo và chạy các luồng
    threads = []
    for handler in device_handlers:
        t = threading.Thread(target=handler.run, args=(2,), daemon=True)  # 2 rounds mỗi thiết bị
        t.start()
        threads.append(t)

    # Đợi tất cả các luồng hoàn thành
    for t in threads:
        t.join()

    print("\n🎉 Tất cả thiết bị đã hoàn thành công việc!")

if __name__ == "__main__":
    main()
