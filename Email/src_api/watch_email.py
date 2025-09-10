# import time
# import os
# import json
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from filelock import FileLock
# from classSend import run_sent
# from classHtmlRender import run_simulator

# # --- Cấu hình biến truyền vào api ---
# EMP_ID = 22616467
# SUBJECT = ""
# CONTENT = ""
# MODE = 1

# # ----------------------------------- #

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BUSINESS_SUBJECT_PATH = os.path.join(BASE_DIR, "business_subject_sample.txt")
# BUSINESS_WRITEN_MAIL_PATH = os.path.join(BASE_DIR, "business_writen_mail_sample.txt")

# JSON_FILE = os.path.join(BASE_DIR, "business_info.json")
# LOCK_FILE = JSON_FILE + ".lock"
# EMAIL_LST_FILE = os.path.join(BASE_DIR, "email_lst.json")

# # --- Debounce ---
# last_trigger = 0
# DEBOUNCE_SEC = 2  # chỉ gọi handler 1 lần nếu file chưa thay đổi trong 2 giây

# # --- Handler khi file JSON thay đổi ---
# class JsonChangeHandler(FileSystemEventHandler):
#     def on_modified(self, event):
#         global last_trigger, SUBJECT, CONTENT
#         if not (event.src_path.endswith("business_info.json") or event.src_path.endswith("email_lst.json")):
#             return

#         now = time.time()
#         if now - last_trigger < DEBOUNCE_SEC:
#             return  # bỏ qua event quá gần nhau
#         last_trigger = now

#         try:
#             with FileLock(LOCK_FILE, timeout=10):
#                 with open(JSON_FILE, "r", encoding="utf-8") as f:
#                     data = json.load(f)
                
#                 emp_id_str = str(EMP_ID)
#                 customers = data.get(emp_id_str, {}).get("customers", [])
#                 has_pending = any(not c.get("sent", False) for c in customers)

#             if has_pending:
#                 print("🔔 Có khách hàng mới, chạy gửi lấy html và gửi mail...")
#                 simulator = run_simulator(EMP_ID, BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH, MODE=MODE)
#                 # set 2 biến nhận từ api
#                 simulator.set_subject(SUBJECT)
#                 simulator.set_content(CONTENT)
#                 simulator.beautify_html()
#                 SUBJECT = simulator.get_subject() # có thể không cần thiết nhưng debug đc
#                 run_sent(EMP_ID, SUBJECT)
#             else:
#                 print("ℹ️ Chưa có khách hàng mới, đợi update tiếp.")
#         except Exception as e:
#             print(f"⚠️ Lỗi khi đọc JSON hoặc gửi mail: {e}")

# # --- Khởi động watcher ---
# if __name__ == "__main__":
#     event_handler = JsonChangeHandler()
#     observer = Observer()
#     observer.schedule(event_handler, BASE_DIR, recursive=False)
#     observer.start()
#     print(f"👂 Đang lắng nghe thay đổi {JSON_FILE} và {EMAIL_LST_FILE} ...")

#     try:
#         while True:
#             time.sleep(5)  
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()
