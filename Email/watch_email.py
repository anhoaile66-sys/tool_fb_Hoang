import time
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from filelock import FileLock
from classSend import run_sent

# --- Cấu hình ---
FILE_BUSINESS = ""
EMP_ID = 22814414
SUBJECT = "Đây là tin nhắn test. Cơ hội việc làm IT dành cho bạn"
CONTENT = (
    "Xin chào, mình là Lại Nhàn đến từ timviec365.vn.\n"
    "Mình thấy bạn có quan tâm đến lĩnh vực IT, "
    "mình muốn giới thiệu bạn một số công việc phù hợp với bạn.\n"
    {FILE_BUSINESS}
    "Bạn có thể xem chi tiết tại đây: https://timviec365.vn/it-cntt-jobs.html.\n\n"
    "Chúc bạn một ngày tốt lành!"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "business_info.json")
LOCK_FILE = JSON_FILE + ".lock"
EMAIL_LST_FILE = os.path.join(BASE_DIR, "email_lst.json")

# --- Debounce ---
last_trigger = 0
DEBOUNCE_SEC = 2  # chỉ gọi handler 1 lần nếu file chưa thay đổi trong 2 giây

# --- Handler khi file JSON thay đổi ---
class JsonChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_trigger
        if not (event.src_path.endswith("business_info.json") or event.src_path.endswith("email_lst.json")):
            return

        now = time.time()
        if now - last_trigger < DEBOUNCE_SEC:
            return  # bỏ qua event quá gần nhau
        last_trigger = now

        try:
            with FileLock(LOCK_FILE, timeout=10):
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                emp_id_str = str(EMP_ID)
                customers = data.get(emp_id_str, {}).get("customers", [])
                has_pending = any(not c.get("sent", False) for c in customers)

            if has_pending:
                print("🔔 Có khách hàng mới, chạy gửi email...")
                run_sent(EMP_ID, SUBJECT, CONTENT)
            else:
                print("ℹ️ Chưa có khách hàng mới, đợi update tiếp.")
        except Exception as e:
            print(f"⚠️ Lỗi khi đọc JSON hoặc gửi mail: {e}")

# --- Khởi động watcher ---
if __name__ == "__main__":
    event_handler = JsonChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, BASE_DIR, recursive=False)
    observer.start()
    print(f"👂 Đang lắng nghe thay đổi {JSON_FILE} và {EMAIL_LST_FILE} ...")

    try:
        while True:
            time.sleep(5)  
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
