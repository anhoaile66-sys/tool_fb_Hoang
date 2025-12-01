import asyncio
import os
from datetime import datetime
from uiautomator2 import Direction
from typing import Optional


# ---------------------------------------------------------------------
# 1. GỬI TIN NHẮN THOẠI
# ---------------------------------------------------------------------
async def send_voice_message(driver, friend_name: str, duration: int = 5):
    try:
        print(f"Sending voice message to {friend_name}...")
        driver(text="Tìm kiếm").click()
        await asyncio.sleep(1)
        driver.send_keys(friend_name)
        await asyncio.sleep(1)
        driver(text=friend_name).click()

        mic_button = driver(description="Gửi tin nhắn thoại")
        mic_button.long_click(duration=duration)
        await asyncio.sleep(duration + 1)

        print(f"Sent voice message to {friend_name}.")
    except Exception as e:
        print(f"Error sending voice message: {e}")


# ---------------------------------------------------------------------
# 2. TẠO NHÓM & NHẮN TIN TRONG NHÓM
# ---------------------------------------------------------------------
async def create_group_chat(driver, group_name: str, members: list):
    try:
        print(f"Creating group {group_name} with {len(members)} members...")
        driver(text="Tin nhắn mới").click()
        await asyncio.sleep(1)
        driver(text="Tạo nhóm").click()

        for name in members:
            driver(text=name).click()
            await asyncio.sleep(0.5)

        driver(text="Tiếp tục").click()
        await asyncio.sleep(1)
        driver(text="Đặt tên nhóm").send_keys(group_name)
        driver(text="Tạo nhóm").click()
        await asyncio.sleep(2)

        print(f"Group {group_name} created.")
    except Exception as e:
        print(f"Error creating group: {e}")


async def send_message_to_group(driver, group_name: str, message: str):
    try:
        driver(text="Tìm kiếm").click()
        await asyncio.sleep(1)
        driver.send_keys(group_name)
        await asyncio.sleep(1)
        driver(text=group_name).click()
        await asyncio.sleep(1)

        driver.send_keys(message)
        driver(description="Gửi").click()
        print(f"Sent message to group {group_name}.")
    except Exception as e:
        print(f"Error sending to group: {e}")


# ---------------------------------------------------------------------
# 3. ĐỒNG BỘ DANH BẠ
# ---------------------------------------------------------------------
async def sync_contacts(driver):
    try:
        print("Syncing contacts...")
        driver(text="Danh bạ").click()
        await asyncio.sleep(1)
        if driver(text="Đồng bộ danh bạ").exists:
            driver(text="Đồng bộ danh bạ").click()
        await asyncio.sleep(2)
        print("Contacts synced.")
    except Exception as e:
        print(f"Error syncing contacts: {e}")


# ---------------------------------------------------------------------
# 4. THẢ TIM, CHIA SẺ
# ---------------------------------------------------------------------
async def react_to_post(driver, friend_name: str):
    try:
        print(f"Liking post of {friend_name}...")
        driver(text="Nhật ký").click()
        await asyncio.sleep(2)
        driver(text=friend_name).click()
        await asyncio.sleep(2)
        driver(description="Thả tim").click()
        print(f"Liked post of {friend_name}.")
    except Exception as e:
        print(f"Error liking post: {e}")


async def share_post(driver):
    try:
        driver(description="Chia sẻ").click()
        await asyncio.sleep(1)
        driver(text="Chia sẻ ngay").click()
        print("Shared post.")
    except Exception as e:
        print(f"Error sharing post: {e}")


# ---------------------------------------------------------------------
# 5. ĐĂNG BÀI LÊN NHẬT KÝ
# ---------------------------------------------------------------------
async def post_to_timeline(driver, content: str, media_path: str = None):
    try:
        driver(text="Nhật ký").click()
        await asyncio.sleep(1)
        driver(description="Tạo bài viết mới").click()
        await asyncio.sleep(1)
        driver.send_keys(content)
        if media_path and os.path.exists(media_path):
            driver(description="Thêm ảnh hoặc video").click()
            driver(text="Chọn từ thư viện").click()
            driver(text=os.path.basename(media_path)).click()
        driver(text="Đăng").click()
        print("Posted to timeline.")
    except Exception as e:
        print(f"Error posting: {e}")


# ---------------------------------------------------------------------
# 6. TỰ ĐỘNG ĐĂNG VIDEO HOT
# ---------------------------------------------------------------------
async def auto_post_hot_video(driver, video_folder: str):
    try:
        videos = [v for v in os.listdir(video_folder) if v.endswith(('.mp4', '.mov'))]
        if not videos:
            print("No video found.")
            return
        video = os.path.join(video_folder, videos[0])
        caption = f"Video hot hôm nay ({datetime.now().strftime('%d/%m/%Y')})"
        await post_to_timeline(driver, caption, media_path=video)
    except Exception as e:
        print(f"Error auto-posting video: {e}")


# =====================================================================
# 7. MỚI: THU HỒI, GHIM, ĐÁNH DẤU TIN NHẮN
# =====================================================================

async def _open_chat(driver, contact_name: str, timeout: int = 10):
    """Mở cuộc trò chuyện với contact_name"""
    try:
        driver(text="Tìm kiếm").click()
        await asyncio.sleep(1)
        driver.send_keys(contact_name)
        await asyncio.sleep(1.5)
        if driver(text=contact_name).wait(timeout=timeout):
            driver(text=contact_name).click()
            await asyncio.sleep(2)
            return True
        else:
            print(f"Không tìm thấy {contact_name} trong danh sách.")
            return False
    except Exception as e:
        print(f"Lỗi mở chat: {e}")
        return False


async def recall_message(
    driver,
    contact_name: str,
    message_text: str,
    timeout: int = 15
):
    """
    Thu hồi tin nhắn đã gửi (chỉ hoạt động trong 2 phút sau khi gửi).
    """
    print(f"Đang thu hồi tin nhắn cho {contact_name}: '{message_text}'")
    try:
        if not await _open_chat(driver, contact_name):
            return False

        # Tìm tin nhắn chứa nội dung
        msg = driver(textContains=message_text).wait(timeout=timeout)
        if not msg:
            print("Không tìm thấy tin nhắn để thu hồi.")
            return False

        msg.long_click()
        await asyncio.sleep(1)

        # Chọn "Thu hồi"
        if driver(text="Thu hồi").exists:
            driver(text="Thu hồi").click()
            await asyncio.sleep(1)
            # Xác nhận "Xóa cho mọi người"
            if driver(text="Xóa cho mọi người").exists:
                driver(text="Xóa cho mọi người").click()
                print("Đã thu hồi tin nhắn thành công.")
                return True
            else:
                print("Không có tùy chọn 'Xóa cho mọi người'.")
                return False
        else:
            print("Không thấy nút 'Thu hồi' (có thể quá 2 phút).")
            return False

    except Exception as e:
        print(f"Lỗi thu hồi tin nhắn: {e}")
        return False


async def pin_message(
    driver,
    contact_name: str,
    message_text: str,
    timeout: int = 10
):
    """
    Ghim tin nhắn lên đầu cuộc trò chuyện.
    """
    print(f"Đang ghim tin nhắn: '{message_text}'")
    try:
        if not await _open_chat(driver, contact_name):
            return False

        msg = driver(textContains=message_text).wait(timeout=timeout)
        if not msg:
            print("Không tìm thấy tin nhắn để ghim.")
            return False

        msg.long_click()
        await asyncio.sleep(1)

        if driver(text="Ghim").exists:
            driver(text="Ghim").click()
            await asyncio.sleep(1)
            print("Đã ghim tin nhắn.")
            return True
        else:
            print("Không thấy nút 'Ghim'.")
            return False

    except Exception as e:
        print(f"Lỗi ghim tin nhắn: {e}")
        return False


async def star_message(
    driver,
    contact_name: str,
    message_text: str,
    timeout: int = 10
):
    """
    Đánh dấu sao (star) tin nhắn để lưu vào mục "Tin nhắn đã đánh dấu".
    """
    print(f"Đang đánh dấu sao tin nhắn: '{message_text}'")
    try:
        if not await _open_chat(driver, contact_name):
            return False

        msg = driver(textContains=message_text).wait(timeout=timeout)
        if not msg:
            print("Không tìm thấy tin nhắn để đánh dấu.")
            return False

        msg.long_click()
        await asyncio.sleep(1)

        # Một số phiên bản Zalo dùng icon sao, một số dùng text
        if driver(text="Đánh dấu sao").exists:
            driver(text="Đánh dấu sao").click()
        elif driver(description="Đánh dấu sao").exists:
            driver(description="Đánh dấu sao").click()
        else:
            print("Không thấy nút đánh dấu sao.")
            return False

        await asyncio.sleep(1)
        print("Đã đánh dấu sao tin nhắn.")
        return True

    except Exception as e:
        print(f"Lỗi đánh dấu sao: {e}")
        return False


# =====================================================================
# 8. HỖ TRỢ: KIỂM TRA TIN NHẮN ĐÃ ĐÁNH DẤU (TÙY CHỌN)
# =====================================================================
async def view_starred_messages(driver):
    """Mở mục 'Tin nhắn đã đánh dấu'"""
    try:
        print("Đang mở tin nhắn đã đánh dấu...")
        driver.press("back")  # Thoát chat nếu đang trong
        await asyncio.sleep(1)
        driver(text="Tôi").click()
        await asyncio.sleep(1)
        driver(text="Tin nhắn đã đánh dấu").click()
        await asyncio.sleep(2)
        print("Đã mở mục tin nhắn đã đánh dấu.")
    except Exception as e:
        print(f"Lỗi mở tin nhắn đã đánh dấu: {e}")