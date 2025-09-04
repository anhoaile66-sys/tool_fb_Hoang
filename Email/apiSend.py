from classSend import run_sent
import time
'''File này chỉ đụng đến nếu watchdog chiếm quá nhiều CPU'''

# --- Config động ---
EMP_ID = 22789191
CONTENT = (
    "Xin chào, mình là Lại Nhàn đến từ timviec365.vn.\n"
    "Mình thấy bạn có quan tâm đến lĩnh vực IT, "
    "mình muốn giới thiệu bạn một số công việc phù hợp với bạn.\n"
    "Bạn có thể xem chi tiết tại đây: https://timviec365.vn/it-cntt-jobs.html.\n\n"
    "Chúc bạn một ngày tốt lành!"
)
SUBJECT = "Đây là tin nhắn test. Cơ hội việc làm IT dành cho bạn"
# --- ---

while True:
    run_sent(EMP_ID, SUBJECT, CONTENT)
    print("⏳ Chờ 1p  trước khi chạy  tiếp theo...")
    time.sleep(60)