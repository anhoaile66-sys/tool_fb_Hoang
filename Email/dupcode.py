# giả sử đã có code email (khi nào dùng thật báo a Cả)
# giả sử đã có nội dung nhắn (khi nào cần thật thì lấy từ CRM??? đã có đâu)

import uiautomator2 as u2
import time

# ID_DEVICE = "9PAM7DIFW87DOBEU"
ID_DEVICE = "F6NZ5LRKWWGACYQ8"

# --- Config ---
CUSTOMER_EMAIL = "vdtimviec@gmail.com"
CONTENT = (
    "Xin chào, mình là Ngô Dung đến từ timviec365.vn.\n"
    "Mình thấy bạn có quan tâm đến lĩnh vực IT, "
    "mình muốn giới thiệu bạn một số công việc phù hợp với bạn.\n"
    "Bạn có thể xem chi tiết tại đây: https://timviec365.vn/it-cntt-jobs.html.\n\n"
    "Chúc bạn một ngày tốt lành!"
)
SUBJECT = "Đây là tin nhắn test. Cơ hội việc làm IT dành cho bạn"

# --- Connect to device ---
d = u2.connect(ID_DEVICE)

# --- Pipeline Gmail ---
def send_email():
    # Nếu chưa ở trong Gmail thì mở Gmail
    current_app = d.app_current()
    if current_app["package"] == "com.google.android.gm":
        print("✅ Đã ở trong Gmail, bỏ qua bước mở app")
        pass
    else:

        d(resourceId="com.android.systemui:id/center_group").click()
        # vuốt lên ??
        d.swipe_ext("up", scale=0.8)  
        time.sleep(2)
        d(resourceId="com.gogo.launcher:id/search_container_all_apps").click()
        time.sleep(2)
        d.send_keys("Gmail", clear=True)
        time.sleep(2)
        d.xpath('//*[@resource-id="com.gogo.launcher:id/branch_suggest_app_list_rv"]/android.view.ViewGroup[1]/android.widget.ImageView[1]').click()
        time.sleep(3)
        print("📩 Đang mở Gmail...")
        # TH2:
        # d(resourceId="com.gogo.launcher:id/icon", text="Gmail").click()
        # time.sleep(3)

    # Nhấn nút soạn mail mới
    d(resourceId="com.google.android.gm:id/compose_button").click()
    time.sleep(1)

    # Nhập email người nhận
    receiver = d.xpath(
        '//*[@resource-id="com.google.android.gm:id/peoplekit_autocomplete_chip_group"]/android.widget.EditText[1]'
    )
    receiver.set_text(CUSTOMER_EMAIL)
    time.sleep(1)

    # Chọn suggestion để đóng chip email
    d.xpath(
        '//*[@resource-id="com.google.android.gm:id/peoplekit_listview_flattened_row"]/android.widget.RelativeLayout[2]'
    ).click()
    time.sleep(1)

    # Nhập tiêu đề
    d(resourceId="com.google.android.gm:id/subject").set_text(SUBJECT)
    time.sleep(1)

    # Nhập nội dung
    d(resourceId="com.google.android.gm:id/composearea_tap_trap_bottom").click()
    d.send_keys(CONTENT, clear=True)
    time.sleep(1)

    # Nhấn gửi
    d(resourceId="com.google.android.gm:id/send").click()
    print("✅ Email đã được gửi thành công!")

# --- Run ---
if __name__ == "__main__":
    send_email()
