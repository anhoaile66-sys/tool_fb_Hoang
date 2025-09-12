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
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re


# ===================== CẤU HÌNH / HẰNG SỐ =====================
# {device_id: [list tên tài khoản đã dùng trong phiên chạy]}
USED_ACCOUNTS = {}
# {device_id: [list tên tài khoản hiển thị lần gần nhất]}
ACCOUNT_CANDIDATES = {}

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
    22889521: "Ngọc Mai",
    22814414: "Bích Ngọc",
}
DATABASE_IDS = list(DATABASE_MAPPING.keys())

# ============ THÊM MAPPING THIẾT BỊ -> DATABASE THEO YÊU CẦU ============
# Lưu ý: các device KHÔNG có trong map này sẽ mặc định dùng Ngô Dung (22615833)
DEVICE_TO_DATABASE = {
    
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
    "Z5LVOF4PRGXGTS9H": 22814414,  # Bích Ngọc
    "EY5H9DJNIVNFH6OR": 22896992   # Huyền Trang

}

DEFAULT_DB_ID = 22615833  # Mặc định: Ngô Dung


def get_database_for_device(device_id: str) -> int:
    """Trả về database_id ứng với thiết bị; mặc định Ngô Dung nếu không có map."""
    return DEVICE_TO_DATABASE.get(device_id, DEFAULT_DB_ID)


# ===== GIỚI HẠN AN TOÀN =====
MAX_FRIEND_REQUESTS_PER_ACC = 1  # Số lời mời kết bạn tối đa / tài khoản
MAX_NEW_MESSAGES_PER_ACC = 1   # Số tin nhắn tới người lạ tối đa / tài khoản
DEVICE_IDS = [
    "7HYP4T4XTS4DXKCY",
    "UWJJOJLB85SO7LIZ",
    "2926294610DA007N",
    "7DXCUKKB6DVWDAQO",
    "8HMN4T9575HAQWLN",
    "CEIN4X45I7ZHFEFU",
    "CQIZKJ8P59AY7DHI",
    "EQLNQ8O7EQCQPFXG",
    "MJZDFY896TMJBUPN",
    "TSPNH6GYZLPJBY6X",
    "YH9TSS7XCMPFZHNR",
    "9PAM7DIFW87DOBEU",
    "F6NZ5LRKWWGACYQ8",
    "EM4DYTEITCCYJNFU",
    "EY5H9DJNIVNFH6OR",
    "QK8TEMKZMBYHPV6P",
    "IJP78949G69DKNHM",
    "PN59BMHYPFXCPN8T",
    "EIFYAALRK7U4MRZ9",
    "Z5LVOF4PRGXGTS9H",
    "69QGMN8PXWDYPNIF",
    "69QGMN8PXWDYPNIF",
    "IZDEGA8TFYXWRK9X",
    "R83Y50JZK6A",
    "R8YY70HCNRX",
    "R8YY70F5MKN",
    "1ac1d26f0507"
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
    "Z5LVOF4PRGXGTS9H": 22814414,  # Bích Ngọc
    "EY5H9DJNIVNFH6OR": 22896992   # Huyền Trang
}

# ===== BIẾN DÙNG CHUNG TOÀN CHƯƠNG TRÌNH (ĐỒNG BỘ NHIỀU THIẾT BỊ) =====
file_lock = Lock()                     # Khóa ghi file (log, json)
db_lock = Lock()                       # Khóa nạp dữ liệu cho queue theo DB
db_queues = defaultdict(Queue)         # Hàng đợi theo từng emp_id
db_loaded = set()                      # Đánh dấu DB đã nạp
# Theo dõi những số đã enqueue (tránh trùng)
db_enqueued_phones = defaultdict(set)
STOP_EVENT = threading.Event()         # Có thể dùng để dừng khẩn cấp

# ===================== TIỆN ÍCH =====================

def update_base_document_json(database_name, domain, collection_name, document):
    try:
        #        print(document)
        with open(f'{database_name}/{collection_name}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for id in range(len(data)):
            #            print(document[domain])
            if data[id][domain] == document[domain]:
                # print(1)
                for key in document.keys():
                    data[id][key] = document[key]
                    # print(document[key])
                break
#        print(data)
        with open(f'{database_name}/{collection_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # print(
        #    f"Đã lưu vào database {collection_name}: {data[0]['list_friend'][0]}")
    except Exception as e:
        print(e)
        return False


def get_base_id_zalo_json(database_name, domain, collection_name, document):
    try:
        with open(f'{database_name}/{collection_name}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        cursor = []
        for d in data:
            check_key = True
            for key in document.keys():
                if d[key] != document[key]:
                    print(d[key])
                    print(document[key])
                    check_key = False
                    break
            if check_key:
                cursor.append(d)
        print(check_key)
        return cursor
    except Exception as e:
        return False


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

def get_message_from_api(emp_id):
    """
    Lấy nội dung tin nhắn chào hỏi từ API.
    Nếu có lỗi hoặc API không trả về tin nhắn, hàm sẽ trả về None.
    """
    api_url = "http://43.239.223.19:8148/chao_hoi"
    payload = {"id": str(emp_id)}  # Đảm bảo ID nhân viên là một chuỗi
    
    print(f"[API] Đang lấy tin nhắn cho nhân viên ID: {emp_id}...")
    
    try:
        # Gửi yêu cầu POST với thời gian chờ 10 giây để tránh bị treo
        response = requests.post(api_url, json=payload, timeout=10)
        
        # Kiểm tra nếu yêu cầu không thành công (vd: lỗi 404, 500)
        response.raise_for_status()
        
        data = response.json()
        
        # Lấy nội dung tin nhắn từ phản hồi JSON, giả sử key là 'message'
        # Điều chỉnh lại key nếu cấu trúc API trả về khác
        message = data.get("message")

        if message and isinstance(message, str) and message.strip():
            print(f"[API] ✅ Lấy tin nhắn từ API thành công.")
            return message.strip()
        else:
            print(f"[API] ⚠️ API không trả về nội dung tin nhắn hợp lệ. Dữ liệu nhận được: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[API] ❌ Lỗi kết nối hoặc yêu cầu tới API thất bại: {e}")
        return None
    except json.JSONDecodeError:
        print(f"[API] ❌ Lỗi: Phản hồi từ API không phải là định dạng JSON hợp lệ.")
        return None
    except Exception as e:
        print(f"[API] ❌ Đã xảy ra lỗi không xác định khi lấy tin nhắn: {e}")
        return None
# ===================== API LẤY SỐ =====================


def get_phone_numbers_from_api(emp_ids, size=1, get_fb_link=True):
    """Lấy danh sách số điện thoại từ API cho nhiều emp_ids"""
    payload = {
        "emp_ids": emp_ids if isinstance(emp_ids, list) else [emp_ids],
        "size": 1,
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


def ensure_db_queue_loaded(emp_id, min_batch_size=1):
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
        data = get_phone_numbers_from_api(emp_id, size=1, get_fb_link=True)
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
        self.current_account_index = 0
        self.accounts = []
        # DANH SÁCH BÌNH LUẬN NGẪU NHIÊN
        self.ZALO_COMMENTS = ["Tuyệt vời ạ", "Bài viết hay quá", "❤️", "Cảm ơn bạn đã chia sẻ thông tin hữu ích", "Thả tim", "Wow"]

    def connect(self):
        try:
            print(f"[✅] Kết nối thiết bị {self.device_id} thành công!")
            self.d.press("home")
            time.sleep(1)
            self.cleanup_background_apps()
            return True
        except Exception as e:
            print(
                f"[❌] Không thể kết nối với thiết bị {self.device_id}. Lỗi: {e}")
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

    # ===================== CÁC HÀM CŨ (Đổi tài khoản, xử lý SĐT...) GIỮ NGUYÊN =====================
    # ... (Toàn bộ các hàm từ _read_visible_accounts đến pick_database_for_round được giữ nguyên ở đây) ...
    def _read_visible_accounts(self):
        """
        Đọc 3 tài khoản hiển thị tại màn hình đổi tài khoản:
        xpath gốc: //*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout[i]/android.widget.TextView[2]
        Trả về list tên theo thứ tự.
        """
        names = []
        try:
            rows = self.d.xpath(
                '//*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout').all()
            for idx in range(1, len(rows) + 1):
                tv2 = self.d.xpath(
                    f'//*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout[{idx}]/android.widget.TextView[2]')
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
            _wait(lambda: self.d(resourceId="com.zing.zalo:id/maintab_metab").exists,
                  8, 0.4, "tab Me sau khi mở app")

        try:
            self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
        except Exception as e:
            print(f"[{device_id}] [⚠] Không bấm được tab Me: {e}")

        # B2: bấm avatar (mở danh sách tài khoản)
        if not _wait(lambda: self.d(resourceId="com.zing.zalo:id/avt_right_list_me_tab").exists, 6, 0.3, "avatar xuất hiện"):
            print(
                f"[{device_id}] [⚠] Không tìm thấy avatar để mở danh sách tài khoản.")
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
                self.d.xpath(
                    '//*[@resource-id="com.zing.zalo:id/recycler_view"]').exists
            )
        if not _wait(_accounts_view_exists, 8, 0.4, "danh sách tài khoản hiện ra"):
            print(
                f"[{device_id}] [⚠] Không thấy danh sách tài khoản (recycle/recycler_view).")
            return False

        # Trích 3 tên tài khoản để ghi nhớ
        visible_names = []
        try:
            # Tìm tất cả các UI element chứa tên tài khoản bằng resourceId
            account_name_elements = self.d(resourceId="com.zing.zalo:id/name").all()
            
            # Lặp qua các element tìm được và lấy text của chúng
            for element in account_name_elements:
                try:
                    name = element.get_text().strip()
                    if name:
                        visible_names.append(name)
                except Exception:
                    # Bỏ qua nếu không đọc được text từ một element nào đó
                    pass
        except Exception as e:
            print(f"[{self.device_id}] [⚠] Lỗi khi đọc tên tài khoản: {e}")

        ACCOUNT_CANDIDATES.setdefault(device_id, [])
        ACCOUNT_CANDIDATES[device_id] = visible_names[:]
        print(
            f"[{device_id}] 👥 3 tài khoản hiển thị: {visible_names if visible_names else 'Không đọc được'}")

        clicked = False
        for try_idx in [2, 1, 3]:
            xpath_try = f'//*[@resource-id="com.zing.zalo:id/recycle_view"]/android.widget.LinearLayout[{try_idx}]/android.widget.TextView[2]'
            xpath_alt = f'//*[@resource-id="com.zing.zalo:id/recycler_view"]/android.widget.LinearLayout[{try_idx}]/android.widget.TextView[2]'
            target_xpath = xpath_try if self.d.xpath(
                '//*[@resource-id="com.zing.zalo:id/recycle_view"]').exists else xpath_alt

            if self.d.xpath(target_xpath).exists:
                try:
                    name_try = ""
                    try:
                        name_try = self.d.xpath(
                            target_xpath).get_text().strip()
                    except Exception:
                        pass
                    print(
                        f"[{device_id}] 👉 Chọn tài khoản dòng {try_idx}{f' ({name_try})' if name_try else ''}")
                    self.d.xpath(target_xpath).click()
                    clicked = True
                    break
                except Exception as e:
                    print(f"[{device_id}] [⚠] Click dòng {try_idx} lỗi: {e}")

        if not clicked:
            print(
                f"[{device_id}] [❌] Không click được bất kỳ dòng tài khoản nào (1/2/3).")
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
            print(
                f"[{device_id}] [⚠] Không tìm được nút Hoàn tất. Thử nhấn back rồi vào lại tab Me.")
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

        print(
            f"[{device_id}] ✅ Hoàn tất đổi tài khoản. Đã reset quota cho tài khoản mới.")
        time.sleep(2)
        return True
    
    def change_contact_name(self, phone_number, contact_info):
        """Đổi tên gợi nhớ cho số điện thoại"""
        try:
            cv_title = (contact_info.get("cv_title") or "").strip()
            name = (contact_info.get("name") or "").strip()
            new_name = f"{cv_title if cv_title else ' '} {name if name else ' '}".strip(
            )

            print(
                f"[{self.device_id}][✏️] Đang đổi tên {phone_number} thành '{new_name}'")
            self.d.app_start("com.zing.zalo", stop=True)
            random_delay(3, 5)

            self.d(text="Tìm kiếm").click()
            random_delay()
            self.d(resourceId="com.zing.zalo:id/global_search_edt").click()
            self.d.send_keys(phone_number, clear=True)
            random_delay(2, 3)

            if not self.d(resourceId="com.zing.zalo:id/btn_search_result").exists:
                print(
                    f"[{self.device_id}][⚠️] Không tìm thấy {phone_number} để đổi tên")
                self.d.press("back")
                return False

            self.d(resourceId="com.zing.zalo:id/btn_search_result").click()
            random_delay(2, 4)

            self.d.xpath(
                '//*[@resource-id="com.zing.zalo:id/zalo_action_bar"]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]').click()
            random_delay()

            self.d.xpath(
                '//*[@resource-id="com.zing.zalo:id/user_info_list_view"]/android.widget.RelativeLayout[2]').click()
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
            return True, new_name

        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi khi đổi tên {phone_number}: {e}")
            self.d.press("home")
            return False, new_name

    def handle_phone_number(self, phone_number, name=None, sender_name=None, emp_id=None): # THÊM emp_id VÀO ĐÂY
        """Gửi tin nhắn/kết bạn cho một số điện thoại. Trả True nếu đã thao tác."""
        try:
            self.d.app_start("com.zing.zalo", stop=True)
            random_delay(3, 5)

            # Đổi tài khoản nếu đã đạt giới hạn
            if (self.friend_requests_count >= MAX_FRIEND_REQUESTS_PER_ACC or
                    self.new_messages_count >= MAX_NEW_MESSAGES_PER_ACC):
                print(
                    f"[{self.device_id}][⚠️] Đạt giới hạn ({self.friend_requests_count} KB / {self.new_messages_count} TN). Chuyển tài khoản...")
                self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
                time.sleep(0.5)
                name_zalo = self.d(
                   resourceId="com.zing.zalo:id/title_list_me_tab").get_text()
                time.sleep(0.5)
                self.switch_account()
                status = update_base_document_json("Zalo_base", "num_phone_zalo", f"Zalo_data_login_path_{self.device_id}", {
                "name": name_zalo, "status": False})

            # Đọc tên tài khoản zalo hiện tại
            self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
            time.sleep(0.5)
            print("Lần 1")
            name_zalo = self.d(
                resourceId="com.zing.zalo:id/title_list_me_tab").get_text()
            time.sleep(0.5)
            status = update_base_document_json("Zalo_base", "num_phone_zalo", f"Zalo_data_login_path_{self.device_id}", {
                "name": name_zalo, "status": True})
            self.d(resourceId="com.zing.zalo:id/maintab_message").click()
            time.sleep(0.5)
            print("Lần 2")
            self.d(text="Tìm kiếm").click()
            random_delay()

            self.d.send_keys(phone_number, clear=True)
            random_delay(2, 3)

            if not self.d(resourceId="com.zing.zalo:id/btn_search_result").exists:
                print(
                    f"[{self.device_id}][⚠️] Không tìm thấy kết quả cho {phone_number}, bỏ qua.")
                self.d.press("back")
                return False

            self.d(resourceId="com.zing.zalo:id/btn_search_result").click()
            random_delay(2, 4)

            # ===================== ĐOẠN NÂNG CẤP BẮT ĐẦU =====================
            # Ưu tiên lấy tin nhắn từ API
            message = get_message_from_api(emp_id)
            
            # Nếu API lỗi hoặc không trả về tin nhắn, dùng mẫu cũ
            if not message:
                print(f"[{self.device_id}][ fallback ] Lỗi API, sử dụng tin nhắn mẫu mặc định.")
                message = get_message_template(sender_name)
            # ===================== ĐOẠN NÂNG CẤP KẾT THÚC =====================


            friend_or_not = "yes"
            # Kịch bản 1: Đã là bạn bè
            if self.d(resourceId="com.zing.zalo:id/chatinput_text").exists:
                print(
                    f"[{self.device_id}][✔] {phone_number} -> Đã là bạn bè. Gửi tin nhắn.")
                if self.d(resourceId="com.zing.zalo:id/action_bar_title").exists:
                    name_ntd = self.d(
                        resourceId="com.zing.zalo:id/action_bar_title").get_text()
                    time.sleep(0.1)
                self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                self.d.send_keys(message, clear=True)
                random_delay(1, 2)
                if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                    self.d(
                        resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                self.new_messages_count += 1

                # Lưu dữ liệu vào database

            # Kịch bản 2: Đã gửi lời mời
            elif self.d(text="Hủy kết bạn").exists:
                print(
                    f"[{self.device_id}][=] {phone_number} -> Đã gửi lời mời. Gửi thêm tin nhắn.")
                if self.d(resourceId="com.zing.zalo:id/btn_send_message").exists:
                    self.d(resourceId="com.zing.zalo:id/btn_send_message").click()
                    random_delay()
                    if self.d(resourceId="com.zing.zalo:id/action_bar_title").exists:
                        name_ntd = self.d(
                            resourceId="com.zing.zalo:id/action_bar_title").get_text()
                        time.sleep(0.1)
                    self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                    self.d.send_keys(message, clear=True)
                    random_delay(1, 2)
                    if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                        self.d(
                            resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                    self.new_messages_count += 1
                friend_or_not = "added"

            # Kịch bản 3: Chưa kết bạn
            else:
                print(
                    f"[{self.device_id}][!] {phone_number} -> Xử lý như chưa kết bạn.")
                if self.d(resourceId="com.zing.zalo:id/btn_send_message").exists:
                    self.d(resourceId="com.zing.zalo:id/btn_send_message").click()
                    random_delay()
                    if self.d(resourceId="com.zing.zalo:id/action_bar_title").exists:
                        name_ntd = self.d(
                            resourceId="com.zing.zalo:id/action_bar_title").get_text()
                        time.sleep(0.1)
                    if self.d(resourceId="com.zing.zalo:id/chatinput_text").exists:
                        self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                        self.d.send_keys(message, clear=True)
                        random_delay(1, 2)
                        if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                            self.d(
                                resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                            self.new_messages_count += 1
                    random_delay()
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
                    print(
                        f"[{self.device_id}][✓] Đã gửi lời mời kết bạn tới {phone_number}")
                else:
                    print(
                        f"[{self.device_id}][⚠] Không tìm thấy nút gửi lời mời cho {phone_number}")
                friend_or_not = "no"

            # Quay về
            self.d.press("back")
            random_delay()
            self.d.press("back")
            random_delay()
            print("Tên tài khoản hiện tại: ", name_zalo)
            return True, message, friend_or_not, name_zalo, name_ntd

        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi khi xử lý {phone_number}: {e}")
            self.d.press("home")
            time.sleep(2)
            return False, message, friend_or_not, name_zalo

    def extract_profile_info(self, phone_number, original_info):
        """Trích xuất thông tin profile Zalo và kết hợp với dữ liệu gốc"""
        print(
            f"\n[{self.device_id}][*] Bắt đầu trích xuất thông tin cho {phone_number}...")
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
                print(
                    f"[{self.device_id}][!] Không tìm thấy {phone_number} để trích xuất")
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
                print(
                    f"[{self.device_id}][i] Đã xử lý và mã hóa avatar thành công.")

            else:
                print(
                    f"[{self.device_id}][!] Không tìm thấy khung avatar cho {zalo_name}")
            profile_data["ava"] = avatar_b64

            self.d.press("back")
            time.sleep(1)

            return profile_data

        except Exception as e:
            print(
                f"[{self.device_id}][❌] Lỗi khi trích xuất thông tin của {phone_number}: {e}")
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
                        all_profiles[i] = profile
                        found = True
                        break
                if not found:
                    all_profiles.append(profile)

                with open(JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_profiles, f, ensure_ascii=False, indent=4)
                print(f"[{self.device_id}][💾] Đã ghi JSON ngay cho {phone}")
                return True
        except Exception as e:
            print(
                f"[{self.device_id}][❌] Lỗi ghi JSON cho {profile.get('phone')}: {e}")
            return False

    def process_phone_number(self, phone_number, contact_info, sender_name, emp_id): # THÊM emp_id
        """Xử lý hoàn chỉnh một số điện thoại"""
        if already_sent(phone_number):
            print(f"[{self.device_id}][⏭] Bỏ qua {phone_number} (đã có trong log)")
            return
        #if True:
        try:
            # 1) Nhắn tin/ gửi kết bạn
            # TRUYỀN emp_id VÀO HÀM NÀY
            interacted, message, friend_or_not, name_zalo, name_ntd = self.handle_phone_number(
                phone_number, contact_info.get("name", ""), sender_name, emp_id)
            print("Có chạy đến hàm lưu dữ liệu không")
            if not interacted:
                print(
                    f"[{self.device_id}][⚠️] Bỏ qua đổi tên & lưu JSON cho {phone_number} vì không tương tác được")
                random_delay(3, 5)
                return

            # 2) Đổi tên gợi nhớ NGAY
            status, new_name = self.change_contact_name(
                phone_number, contact_info)

            # 3) Trích xuất profile NGAY
            profile_data = self.extract_profile_info(
                phone_number, contact_info)

            # 4) Ghi ra file JSON phục vụ CRM
            document = get_base_id_zalo_json("Zalo_base", "name", f"Zalo_data_login_path_{self.device_id}", {
                "name": name_zalo})[0]
            #print("Phần tử được lấy ra là: ", document)
            print("Đã lấy file base thành công ", f"Zalo_data_login_path_{self.device_id}")
            # Lấy ra thời gian gửi tin nhắn
            now = datetime.now()
            print("Ngày:", now.day)
            print("Tháng:", now.month)
            print("Năm:", now.year)
            print("Giờ:", now.hour)
            print("Phút:", now.minute)
            print("Giây:", now.second)
            hour = str(now.hour)
            minute = str(now.hour)
            if len(hour) == 1:
                hour = f"0{hour}"
            if len(minute) == 1:
                minute = f"0{minute}"
            time_str = f"{hour}:{minute} {now.day}/{now.month}/{now.year}"

            list_prior_chat_boxes = document['list_prior_chat_boxes']

            check = False
            for id in range(len(list_prior_chat_boxes)):
                if list_prior_chat_boxes[id]['name'] == name_ntd:
                    check = True
                    if 'data_chat_box' not in list_prior_chat_boxes[id].keys():
                        print("Có khôngs")
                        list_prior_chat_boxes[id]['data_chat_box'] = []

                    list_prior_chat_boxes[id]['time'] = time_str
                    list_prior_chat_boxes[id]['message'] = message
                    list_prior_chat_boxes[id]['status'] = "seen"
                    if profile_data['ava']:
                       list_prior_chat_boxes[id]['ava'] = profile_data['ava']
                    list_prior_chat_boxes[id]['data_chat_box'].append(
                        {"you": [{'time': time_str, 'type': "text", "data": message}]})
                    list_prior_chat_boxes[id]['friend_or_not'] = friend_or_not
                    list_prior_chat_boxes.insert(
                        0, list_prior_chat_boxes.pop(id))

                    break

            if not check:
                '''
                num = message.split(" ")
                if len(num) > 10:
                    num = num[:10]
                    message = " ".join(num)
                '''    
                list_prior_chat_boxes.append(
                    {"name": name_ntd, "time": time_str, "message": message, "ava": profile_data['ava'], "tag": "", "status": "seen", "data_chat_box": [], "friend_or_not": friend_or_not})
                list_prior_chat_boxes[-1]['data_chat_box'].append(
                    {"you": [{'time': time_str, 'type': "text", "data": message}]})
                list_prior_chat_boxes.insert(
                    0, list_prior_chat_boxes.pop(-1))

            data_update = {"name": name_zalo,
                           "list_prior_chat_boxes": list_prior_chat_boxes}
            update_base_document_json(
                "Zalo_base", "name", f"Zalo_data_login_path_{self.device_id}", data_update)
            print("Đã lưu vào database ", f"Zalo_data_login_path_{self.device_id}")

            # 5) Ghi JSON NGAY (upsert)
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

    # ===================== TÍNH NĂNG: CHÚC MỪNG SINH NHẬT =====================
    def send_birthday_wishes(self):
        """
        Kiểm tra và gửi lời chúc mừng sinh nhật cho bạn bè có sinh nhật hôm nay.
        """
        print(f"\n[{self.device_id}]🎂 Bắt đầu kiểm tra sinh nhật...")
        
        # --- Lấy thông tin tài khoản Zalo hiện tại ---
        current_account_name = ""
        try:
            self.d.app_start("com.zing.zalo", stop=True)
            time.sleep(5)
            if self.d(resourceId="com.zing.zalo:id/maintab_metab").exists:
                self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
                time.sleep(1.5)
                if self.d(resourceId="com.zing.zalo:id/title_list_me_tab").exists:
                    current_account_name = self.d(resourceId="com.zing.zalo:id/title_list_me_tab").get_text().strip()
                self.d(resourceId="com.zing.zalo:id/maintab_message").click() # Quay về tab tin nhắn
                time.sleep(1)
        except Exception as e:
            print(f"[{self.device_id}][⚠️] Không thể lấy tên tài khoản Zalo hiện tại: {e}")
            self.d.press("home")
            return

        if not current_account_name:
            print(f"[{self.device_id}][❌] Không có tên tài khoản Zalo, không thể kiểm tra sinh nhật.")
            return
            
        print(f"[{self.device_id}][ℹ️] Tài khoản hiện tại: {current_account_name}")

        # --- Đọc dữ liệu từ file JSON của thiết bị ---
        account_data = None
        try:
            # Ưu tiên đọc file theo ID thiết bị
            json_file = f"Zalo_data_login_path_{self.device_id}.json"  ##note1
            if not os.path.exists(json_file):
                 # Nếu không có, thử đọc file mà người dùng cung cấp
                 json_file = "Zalo_data_login_path_YH9TSS7XCMPFZHNR.json"
                 if not os.path.exists(json_file):
                    print(f"[{self.device_id}][❌] Không tìm thấy file dữ liệu: {json_file}")
                    return

            with open(json_file, 'r', encoding='utf-8') as f:
                all_accounts = json.load(f)
            
            for acc in all_accounts:
                if acc.get("name") == current_account_name:
                    account_data = acc
                    break
        except Exception as e:
            print(f"[{self.device_id}][❌] Lỗi khi đọc file JSON: {e}")
            return

        if not account_data or 'list_friend' not in account_data:
            print(f"[{self.device_id}][ℹ️] Không có dữ liệu bạn bè cho tài khoản {current_account_name}.")
            return

        # --- Tìm bạn bè có sinh nhật hôm nay ---
        today_str = datetime.now().strftime("%d/%m")
        birthday_friends = []
        for friend in account_data.get('list_friend', []):
            dob = friend.get('day_of_birth', '')
            if dob and dob.startswith(today_str):
                birthday_friends.append(friend)
        
        if not birthday_friends:
            print(f"[{self.device_id}][ℹ️] Hôm nay không có sinh nhật bạn bè nào.")
            return

        print(f"[{self.device_id}][🎉] Tìm thấy {len(birthday_friends)} bạn có sinh nhật hôm nay: {[f.get('name') for f in birthday_friends]}")

        # --- Quản lý log và gửi lời chúc ---
        log_file_today = f"birthday_log_{datetime.now().strftime('%Y-%m-%d')}.txt"
        sent_today = set()
        try:
            with open(log_file_today, 'r', encoding='utf-8') as f:
                sent_today = {line.strip() for line in f}
        except FileNotFoundError:
            pass # Bỏ qua nếu file chưa tồn tại

        birthday_wishes = [
            "Chúc mừng sinh nhật bạn!",
            "Chúc bạn tuổi mới nhiều niềm vui, hạnh phúc và thành công nhé!",
            "Sinh nhật vui vẻ nha bạn ơi!",
            "Happy Birthday! Chúc bạn mọi điều tốt lành."
        ]
        
        for friend in birthday_friends:
            friend_name = friend.get('name')
            # Bỏ qua nếu không có tên hoặc đã gửi rồi
            if not friend_name or friend_name in sent_today:
                print(f"[{self.device_id}][⏭️] Bỏ qua {friend_name} (tên rỗng hoặc đã gửi).")
                continue

            print(f"[{self.device_id}]--> Chuẩn bị gửi lời chúc đến {friend_name}")
            try:
                # Yêu cầu: Khởi động lại app cho mỗi lần gửi
                self.cleanup_background_apps()
                self.d.app_start("com.zing.zalo", stop=True)
                random_delay(5, 7)
                
                # Thực hiện chuỗi hành động gửi tin nhắn theo yêu cầu
                self.d(text="Tìm kiếm").click()
                random_delay()
                self.d(resourceId="com.zing.zalo:id/global_search_edt").click()
                self.d.send_keys(friend_name, clear=True) # Tìm theo tên bạn bè
                random_delay()
                
                if self.d(resourceId="com.zing.zalo:id/btn_search_result").exists:
                    self.d(resourceId="com.zing.zalo:id/btn_search_result").click()
                    random_delay()
                else:
                    print(f"[{self.device_id}][⚠️] Không tìm thấy kết quả cho '{friend_name}'.")
                    self.d.press("back")
                    continue
                
                if self.d(resourceId="com.zing.zalo:id/btn_send_message").exists:
                    self.d(resourceId="com.zing.zalo:id/btn_send_message").click()
                    random_delay()

                if not self.d(resourceId="com.zing.zalo:id/chatinput_text").exists(timeout=5):
                    print(f"[{self.device_id}][⚠️] Không thể vào màn hình chat với {friend_name}.")
                    self.d.press("home")
                    continue

                # Gửi sticker
                self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                self.d.send_keys("Chúc mừng sinh nhật!", clear=True)
                random_delay(2, 3) # Chờ sticker load
                if self.d.xpath('//*[@resource-id="com.zing.zalo:id/search_inline_listview"]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.FrameLayout[1]').exists:
                    self.d.xpath('//*[@resource-id="com.zing.zalo:id/search_inline_listview"]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.FrameLayout[1]').click()
                    random_delay()
                
                # Gửi tin nhắn text
                self.d(resourceId="com.zing.zalo:id/chatinput_text").click()
                self.d.send_keys(random.choice(birthday_wishes), clear=True)
                random_delay()
                if self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").exists:
                    self.d(resourceId="com.zing.zalo:id/new_chat_input_btn_chat_send").click()
                
                print(f"[{self.device_id}][✅] Đã gửi lời chúc mừng sinh nhật đến {friend_name}")
                
                # Ghi log để không gửi lại
                with file_lock, open(log_file_today, 'a', encoding='utf-8') as f:
                    f.write(f"{friend_name}\n")
                
                random_delay(3, 5) 
                self.d.press("home")
                
            except Exception as e:
                print(f"[{self.device_id}][❌] Lỗi khi gửi lời chúc cho {friend_name}: {e}")
                self.d.press("home")
                continue
        
        print(f"[{self.device_id}]🎂 Hoàn tất kiểm tra và gửi lời chúc sinh nhật.")
        self.cleanup_background_apps()

    # ===================== CÁC HÀM LƯỚT ZALO (TỪ NOTEBOOK) =====================
    def like_posts_in_current_frame(self):
        print(f"[{self.device_id}] Đang tìm nút 'Thích'...")
        xml_dump = self.d.dump_hierarchy()
        root = ET.fromstring(xml_dump)
        like_buttons = []
        for node in root.iter():
            if (node.attrib.get("resource-id") == "com.zing.zalo:id/btn_like" and 
                node.attrib.get("bounds") and 
                node.attrib.get("clickable") == "true"):
                like_buttons.append(node.attrib.get("bounds"))
        
        if not like_buttons:
            print(f"[{self.device_id}] ❌ Không tìm thấy nút thích nào.")
            return 0

        # Thích 1 bài viết ngẫu nhiên để trông tự nhiên hơn
        bounds_to_like = random.choice(like_buttons)
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_to_like)
        if m:
            left, top, right, bottom = map(int, m.groups())
            center_x, center_y = (left + right) // 2, (top + bottom) // 2
            try:
                print(f"[{self.device_id}] 👍 Thích bài viết tại ({center_x}, {center_y})")
                self.d.click(center_x, center_y)
                time.sleep(random.uniform(1, 2))
                return 1
            except Exception as e:
                print(f"[{self.device_id}]  Lỗi khi bấm nút thích: {e}")
        return 0

    def comment_on_posts_in_current_frame(self, comment_text="Hay quá"):
        print(f"[{self.device_id}] Đang tìm nút 'Bình luận'...")
        xml_dump = self.d.dump_hierarchy()
        root = ET.fromstring(xml_dump)
        
        comment_buttons = []
        for node in root.iter():
            rid = node.attrib.get("resource-id", "")
            if ((rid == "com.zing.zalo:id/comment_component" or rid == "com.zing.zalo:id/btn_comment") and 
                node.attrib.get("bounds") and node.attrib.get("clickable") == "true"):
                comment_buttons.append(node.attrib.get("bounds"))

        if not comment_buttons:
            print(f"[{self.device_id}] ❌ Không tìm thấy nút bình luận nào.")
            return 0
        
        # Chọn một nút bình luận ngẫu nhiên
        bounds = random.choice(comment_buttons)
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
        if not m:
            return 0

        left, top, right, bottom = map(int, m.groups())
        center_x, center_y = (left + right) // 2, (top + bottom) // 2
        
        try:
            print(f"[{self.device_id}] 💬 Mở form bình luận...")
            self.d.click(center_x, center_y)
            time.sleep(3)

            # Nhập và gửi bình luận
            if self.d(resourceId="com.zing.zalo:id/cmtinput_text").exists(timeout=5):
                self.d(resourceId="com.zing.zalo:id/cmtinput_text").click()
                time.sleep(1)
                self.d.send_keys(comment_text)
                print(f"[{self.device_id}] Đã nhập: '{comment_text}'")
                time.sleep(1)
                if self.d(resourceId="com.zing.zalo:id/cmtinput_send").exists:
                    self.d(resourceId="com.zing.zalo:id/cmtinput_send").click()
                    print(f"[{self.device_id}] ✅ Đã gửi bình luận thành công!")
                    time.sleep(3)
                    self.d.press("back") # Đóng form bình luận
                    return 1
            
            print(f"[{self.device_id}] ⚠️ Không tìm thấy ô nhập liệu hoặc nút gửi.")
            self.d.press("back") # Đóng form nếu có lỗi
            return 0

        except Exception as e:
            print(f"[{self.device_id}] ❌ Lỗi khi bình luận: {e}")
            self.d.press("back")
            return 0
 
    # ------------------ BỔ SUNG: LƯỚT TRANG CÁ NHÂN BẠN BÈ ------------------
    # ------------------ QUẢN LÝ LỊCH SỬ FRIENDS VIEWED ------------------
    def load_viewed_friends(self):
        """
        Đọc file lưu bạn bè đã xem profile, tự động xóa entry quá 7 ngày.
        """
        file_path = f"Zalo_friends_viewed_{self.device_id}.json"
        data = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return {}

        # cleanup entries quá hạn
        now = datetime.now()
        new_data = {}
        for name, ts in data.items():
            try:
                ts_dt = datetime.fromisoformat(ts)
                if now - ts_dt <= timedelta(days=7):
                    new_data[name] = ts
            except Exception:
                continue

        if new_data != data:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        return new_data

    def save_viewed_friend(self, friend_name):
        """
        Lưu lại bạn bè vừa được xem profile kèm timestamp.
        """
        file_path = f"Zalo_friends_viewed_{self.device_id}.json"
        try:
            data = self.load_viewed_friends()
            data[friend_name] = datetime.now().isoformat()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[{self.device_id}] ❌ Không thể lưu viewed friend {friend_name}: {e}")
# ---------------------------------------------------------------------

    def surf_friends_profiles(self, duration_minutes=10):
        """
        Vào profile bạn bè theo tên (lấy từ file Zalo_data_login_path_{device_id}.json)
        Lướt và like theo luật:
        - Mỗi friend: lướt tối đa 15 lần
        - Nếu lướt 3 lần liên tiếp mà không thấy bài viết (không thấy nút like) -> dừng sớm cho friend đó
        - Xác suất like mỗi lần thấy nút like: 90%
        - Sau mỗi friend: tắt tất cả tab (cleanup) rồi mở lại Zalo trước khi tìm friend tiếp theo
        - Toàn bộ quá trình không vượt quá duration_minutes (phút)
        Đồng thời lưu danh sách bạn bè đã xem profile để tránh xem trùng trong 7 ngày.
        """
        start_ts = time.time()
        max_seconds = duration_minutes * 60
        base_dir = r"C:\Zalo_CRM\Zalo_base"
        device_json_file = os.path.join(base_dir, f"Zalo_data_login_path_{self.device_id}.json")
        print(f"[{self.device_id}] 🔎 Đọc dữ liệu từ: {device_json_file}")

        # Đọc file dữ liệu để lấy list_friend cho tài khoản hiện tại
        try:
            with open(device_json_file, "r", encoding="utf-8") as f:
                accounts = json.load(f)
        except Exception as e:
            print(f"[{self.device_id}] ❌ Không thể đọc file {device_json_file}: {e}")
            return

        # Lấy tên tài khoản hiện tại trên thiết bị
        try:
            self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
            time.sleep(0.5)
            current_account_name = self.d(resourceId="com.zing.zalo:id/title_list_me_tab").get_text().strip()
        except Exception:
            current_account_name = None

        # Tìm entry trong JSON trùng tên tài khoản (nếu không có tên, fallback: lấy mọi list_friend của device_id)
        friends_list = []
        for entry in accounts:
            if entry.get("id_device") == self.device_id:
                if current_account_name and entry.get("name") == current_account_name:
                    friends_list = entry.get("list_friend", []) or []
                    break
                if not friends_list:
                    friends_list = entry.get("list_friend", []) or []

        if not friends_list:
            print(f"[{self.device_id}] ⚠️ Không tìm thấy bạn bè trong dữ liệu cho account '{current_account_name}'. Bỏ qua.")
            return

        # Load danh sách bạn bè đã xem trong 7 ngày gần nhất
        viewed_friends = self.load_viewed_friends()

        print(f"[{self.device_id}] ℹ️ Bắt đầu lướt trang cá nhân bạn bè: {len(friends_list)} bạn.")

        for friend in friends_list:
            if time.time() - start_ts > max_seconds:
                print(f"[{self.device_id}] ⏱️ Hết thời gian {duration_minutes} phút cho quá trình lướt friends. Dừng.")
                break

            friend_name = friend.get("name")
            if not friend_name:
                continue

            # Bỏ qua nếu friend đã được xem trong 7 ngày qua
            if friend_name in viewed_friends:
                print(f"[{self.device_id}] ⏩ Bỏ qua {friend_name} (đã xem trong 7 ngày qua).")
                continue

            print(f"[{self.device_id}] ▶ Vào trang cá nhân: {friend_name}")

            try:
                # Reset / khởi động lại app để tìm kiếm sạch sẽ
                self.cleanup_background_apps()
                time.sleep(1)
                self.d.app_start("com.zing.zalo")
                time.sleep(2)

                # Tìm kiếm theo tên
                if self.d(text="Tìm kiếm").exists:
                    self.d(text="Tìm kiếm").click()
                elif self.d(resourceId="com.zing.zalo:id/search_text").exists:
                    self.d(resourceId="com.zing.zalo:id/search_text").click()
                else:
                    if self.d(resourceId="com.zing.zalo:id/maintab_message").exists:
                        self.d(resourceId="com.zing.zalo:id/maintab_message").click()
                        time.sleep(0.5)
                        if self.d(text="Tìm kiếm").exists:
                            self.d(text="Tìm kiếm").click()

                time.sleep(0.8)
                self.d.send_keys(friend_name, clear=True)
                time.sleep(1)

                if not self.d(resourceId="com.zing.zalo:id/btn_search_result").exists:
                    print(f"[{self.device_id}] ⚠️ Không tìm thấy kết quả tìm kiếm cho '{friend_name}'. Tiếp.")
                    self.d.press("back")
                    continue

                self.d(resourceId="com.zing.zalo:id/btn_search_result").click()
                time.sleep(1.2)

                if self.d(resourceId="com.zing.zalo:id/action_bar_title").exists:
                    try:
                        self.d(resourceId="com.zing.zalo:id/action_bar_title").click()
                        time.sleep(1.2)
                    except Exception:
                        pass

                # Bắt đầu lướt profile
                no_post_consecutive = 0
                scrolls = 0
                while scrolls < 15 and (time.time() - start_ts) <= max_seconds:
                    likes_done = 0
                    if random.random() < 0.9:
                        likes_done = self.like_posts_in_current_frame()
                    else:
                        print(f"[{self.device_id}] ℹ️ Bỏ qua like do xác suất.")

                    if likes_done:
                        no_post_consecutive = 0
                        print(f"[{self.device_id}] 👍 Đã like 1 bài trên profile {friend_name}.")
                    else:
                        no_post_consecutive += 1
                        print(f"[{self.device_id}] ℹ️ Không thấy post để like (đếm: {no_post_consecutive}).")

                    if no_post_consecutive >= 3:
                        print(f"[{self.device_id}] ℹ️ 3 lần liên tiếp không thấy post -> kết thúc sớm cho {friend_name}.")
                        break

                    self.d.swipe_ext("up", scale=random.uniform(0.55, 0.8))
                    time.sleep(random.uniform(1.2, 2.5))
                    scrolls += 1

                # Sau khi xem xong: lưu lại friend này
                self.save_viewed_friend(friend_name)

                # Dọn app để chuyển sang friend tiếp theo
                print(f"[{self.device_id}] ✅ Xong profile {friend_name}. Dọn background và chuẩn bị profile tiếp.")
                self.cleanup_background_apps()
                time.sleep(random.uniform(1.0, 2.0))
                self.d.app_start("com.zing.zalo")
                time.sleep(1.2)

            except Exception as e:
                print(f"[{self.device_id}] ❌ Lỗi khi lướt profile {friend_name}: {e}")
                try:
                    self.cleanup_background_apps()
                except Exception:
                    pass
                continue

        print(f"[{self.device_id}] 🎯 Hoàn tất lướt trang cá nhân bạn bè (hoặc hết thời gian).")


# -------------------------------------------------------------------------

    def surf_zalo_timeline(self):
        """
        Thực hiện chu trình lướt Zalo Timeline NÂNG CAO, mô phỏng hành vi người dùng thật
        bằng cách kết hợp ngẫu nhiên các hành động: lướt, xem video, thích, và bình luận.
        """
        print(f"\n[{self.device_id}]===== Bắt đầu chu trình lướt Zalo Timeline NÂNG CAO =====")
        try:
            # === PHA 1: KHỞI ĐỘNG LẠI APP ĐỂ ĐẢM BẢO ỔN ĐỊNH ===
            print(f"[{self.device_id}] Đang khởi động lại Zalo để bắt đầu lướt...")
            self.d.app_stop("com.zing.zalo")
            time.sleep(1)
            self.d.app_start("com.zing.zalo")
            time.sleep(5)

            # === PHA 2: ĐIỀU HƯỚNG TỚI TAB NHẬT KÝ ===
            if not self.d(resourceId="com.zing.zalo:id/maintab_timeline").exists:
                print(f"[{self.device_id}] ❌ Không tìm thấy tab Nhật ký. Bỏ qua lướt.")
                return
            self.d(resourceId="com.zing.zalo:id/maintab_timeline").click()
            time.sleep(2)
            print(f"[{self.device_id}] ✅ Đã chuyển đến tab Nhật ký.")

            # === PHA 3: VÒNG LẶP LƯỚT VÀ TƯƠNG TÁC TỰ ĐỘNG ===
            session_minutes = random.randint(3, 5)
            end_time = time.time() + session_minutes * 60
            print(f"[{self.device_id}] ⏳ Phiên lướt sẽ kéo dài trong {session_minutes} phút.")

            while time.time() < end_time:
                # Quyết định hành động tiếp theo (có trọng số)
                action = random.choices(
                    ['scroll', 'like', 'comment', 'watch_video'],
                    weights=[70, 15, 5, 10], k=1
                )[0]
                
                print(f"[{self.device_id}] -> Hành động ngẫu nhiên: {action.upper()}")

                if action == 'like':
                    self.like_posts_in_current_frame()
                
                elif action == 'comment':
                    random_comment = random.choice(self.ZALO_COMMENTS)
                    self.comment_on_posts_in_current_frame(comment_text=random_comment)
                
                elif action == 'watch_video':
                    xml_dump = self.d.dump_hierarchy()
                    root = ET.fromstring(xml_dump)
                    video_node_bounds = None
                    for node in root.iter():
                        rid = node.attrib.get("resource-id", "").lower()
                        if "video" in rid or "videotexturerenderview" in node.attrib.get("class", "").lower():
                            video_node_bounds = node.attrib.get("bounds")
                            break
                    
                    if video_node_bounds:
                        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", video_node_bounds)
                        if m:
                            left, top, right, bottom = map(int, m.groups())
                            watch_duration = random.randint(15, 25)
                            print(f"[{self.device_id}] 🎬 Tìm thấy video, sẽ xem trong {watch_duration} giây...")
                            self.d.click((left + right) // 2, (top + bottom) // 2)
                            time.sleep(watch_duration)
                            self.d.press("back")
                            print(f"[{self.device_id}] Đã xem xong video.")
                    else:
                        print(f"[{self.device_id}] Không thấy video, sẽ lướt tiếp.")
                        self.d.swipe_ext("up", scale=random.uniform(0.6, 0.8))
                else: # Mặc định là 'scroll'
                    self.d.swipe_ext("up", scale=random.uniform(0.6, 0.8))

                # Chờ một lúc trước hành động tiếp theo
                time.sleep(random.uniform(4, 8))
                remaining_time = (end_time - time.time()) / 60
                print(f"[{self.device_id}] 📊 Thời gian lướt còn lại: {remaining_time:.1f} phút.")

            # === PHA 4: KẾT THÚC VÀ DỌN DẸP ===
            print(f"[{self.device_id}] ✅ Hoàn thành phiên lướt. Quay về tab Tin nhắn.")
            if self.d(resourceId="com.zing.zalo:id/maintab_message").exists:
                self.d(resourceId="com.zing.zalo:id/maintab_message").click()
            else:
                self.d.press("back")
            time.sleep(2)

        except Exception as e:
            print(f"[{self.device_id}] ❌ Lỗi trong quá trình lướt Zalo nâng cao: {e}")
            self.d.press("home")

    def run(self, rounds=1):
        """
        Chạy luồng Zalo: (1) Lướt khám phá -> (2) Tìm SĐT & nhắn tin kết bạn -> (3) Lướt trang cá nhân bạn bè -> Đổi TK
        """
        if rounds > 0 and not STOP_EVENT.is_set():
            # Tính năng chúc mừng SN (giữ nguyên như cũ)
            self.send_birthday_wishes()

            print(f"\n[{self.device_id}]===== Bắt đầu chu trình Zalo (Lướt -> SĐT -> Lướt profile -> Đổi TK) =====")
            current_db = self.pick_database_for_round()
            sender_name = DATABASE_MAPPING.get(current_db, "Nhân viên")
            print(f"[{self.device_id}] Lấy việc từ database {current_db} ({sender_name})")

            # PHA 1: Lướt khám phá (Timeline)
            try:
                self.surf_zalo_timeline()
            except Exception as e:
                print(f"[{self.device_id}] ⚠️ Lỗi khi lướt khám phá: {e}")

            # PHA 2: Tìm SĐT và xử lý 1 item (giữ nguyên logic)
            ensure_db_queue_loaded(current_db)
            try:
                contact = db_queues[current_db].get(timeout=5)
                phone_number = (contact.get("phone_number") or "").strip()
                if phone_number:
                    print(f"[{self.device_id}] Xử lý SĐT: {phone_number}")
                    self.process_phone_number(phone_number, contact, sender_name, current_db)
                db_queues[current_db].task_done()
            except Empty:
                print(f"[{self.device_id}] Hàng đợi trống, bỏ qua xử lý SĐT.")
            except Exception as e:
                print(f"[{self.device_id}] Lỗi khi xử lý SĐT: {e}")

            # PHA 3: Lướt trang cá nhân bạn bè (mỗi account 10 phút tối đa)
            try:
                self.surf_friends_profiles(duration_minutes=10)
            except Exception as e:
                print(f"[{self.device_id}] ⚠️ Lỗi khi lướt profile bạn bè: {e}")

            # PHA 4: Đổi tài khoản như cũ
            print(f"[{self.device_id}] Chu trình xong, chuẩn bị đổi tài khoản.")
            try:
                # Restart app & set inactive cho tài khoản cũ như trước
                self.d.app_stop("com.zing.zalo")
                time.sleep(1)
                self.d.app_start("com.zing.zalo")
                time.sleep(5)
                self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
                time.sleep(0.5)
                name_zalo = self.d(resourceId="com.zing.zalo:id/title_list_me_tab").get_text()
                update_base_document_json("Zalo_base", "num_phone_zalo", f"Zalo_data_login_path_{self.device_id}", {
                    "name": name_zalo, "status": False
                })
            except Exception as e:
                print(f"[{self.device_id}] Không thể set trạng thái inactive cho tài khoản cũ: {e}")

            # thực hiện đổi tài khoản
            self.switch_account()

            # set active cho tk mới (giữ logic cũ)
            try:
                self.d(resourceId="com.zing.zalo:id/maintab_metab").click()
                time.sleep(0.5)
                new_name_zalo = self.d(resourceId="com.zing.zalo:id/title_list_me_tab").get_text()
                update_base_document_json("Zalo_base", "name", f"Zalo_data_login_path_{self.device_id}", {
                    "name": new_name_zalo, "status": True
                })
                self.d(resourceId="com.zing.zalo:id/maintab_message").click()
                time.sleep(0.5)
            except Exception as e:
                print(f"[{self.device_id}] Không thể set trạng thái active cho tài khoản mới: {e}")

            print(f"\n[{self.device_id}]🎉 Hoàn tất chu trình Zalo. Quay về luồng chính.")



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
        t = threading.Thread(target=handler.run, args=(
            2,), daemon=True)  # 2 rounds mỗi thiết bị
        t.start()
        threads.append(t)

    # Đợi tất cả các luồng hoàn thành
    for t in threads:
        t.join()

    print("\n🎉 Tất cả thiết bị đã hoàn thành công việc!")


if __name__ == "__main__":
    main()
