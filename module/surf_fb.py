import asyncio
import logging
import json
import random
from util import *
import toolfacebook_lib

EMOTION = [
    "Thích",
    "Yêu thích",
    "Thương thương"
]

COMMENTS = [
    # Nhóm quan tâm, hỏi thông tin
    "Còn tuyển không ạ? 👨‍💼",
    "Vị trí này còn không ạ?",
    "Mình có thể ứng tuyển được không?",
    "Làm sao để apply ạ?",
    "Có yêu cầu kinh nghiệm không ạ?",
    "Lương bao nhiêu vậy ạ?",
    "Thời gian làm việc như thế nào?",
    "Địa điểm làm việc ở đâu ạ?",
    "Có cần bằng cấp gì không?",
    "Mình quan tâm position này ạ 👍",

    # Nhóm thể hiện hứng thú
    "Công việc hay quá! 😍",
    "Phù hợp với mình ghê! 😊",
    "Mình đang tìm việc như này!",
    "Cơ hội tốt quá! 🎯",
    "Công ty có vẻ ổn nhỉ! 😎",
    "Môi trường làm việc tuyệt! 💼",
    "Thử apply xem sao! 🚀",
    "Đúng ngành mình rồi!",
    "Thanks for sharing! 🙏",
    "Cảm ơn info hay! ✨",

    # Nhóm tích cực, professional
    "Cảm ơn bạn đã share!",
    "Thông tin hữu ích quá! 👌",
    "Note lại để apply sau! 📝",
    "Công ty uy tín nhỉ! 🏢",
    "Mong được cơ hội thử! 🤝",
    "Đã gửi CV rồi ạ! 📧",
    "Hy vọng sẽ có cơ hội! 🤞",
    "Up cho mọi người cùng biết! ⬆️",
    "Ai quan tâm thì inbox mình nhé!",
    "Good luck cho ai apply! 🍀"
]

#Thả cảm xúc vào bài viết (Phẫn nộ sẽ đổi thành Buồn, "đấy là tính năng")
async def like_post(driver, emotion="like"):
    """
    Tìm nút like phía dưới, scroll vào màn hình, nhấn like.\n
    Nhấn giữ để hiện bảng emote, kéo thả vào emote tương ứng:
    'Thích', 'Yêu thích', 'Thương Thương', 'Haha', 'Wow', 'Buồn', 'Phẫn nộ'
    """
    log_message("Bắt đầu like post")
    # Tìm nút like
    like_button = await scroll_until_element_visible(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Nút Thích.")]')})
    # Đọc bài viết 1 tí
    await asyncio.sleep(random.uniform(5,15))

    if like_button == None:
        log_message(f"[{driver.serial}] Không thể tìm được nút like", logging.ERROR)
        return
    if emotion == "like":
        like_button.click()
        log_message(f"[{driver.serial}] Đã thả cảm xúc Thích")
        return

    # Chờ menu cảm xúc xuất hiện
    like_button.long_click()
    await asyncio.sleep(random.uniform(1,2))
    
    # Tìm và chọn cảm xúc mong muốn
    emotion_element = await my_find_element(driver, {("xpath", f'//com.facebook.feedback.sharedcomponents.reactions.dock.RopeStyleUFIDockView[@content-desc="{emotion}"]')})
    try:
        emotion_element.click()
        await asyncio.sleep(random.uniform(2,3))
        log_message(f"Đã thả cảm xúc {emotion}")
        return
    except Exception:
        log_message(f"Không tìm được emotion: {emotion}", logging.ERROR)
        return

# Bình luận vào bài viết
async def comment_post(driver, text):
    """
    Tìm nút comment phía dưới, nhấn vào và comment đoạn comment cho trước"""
    log_message("Bắt đầu comment post")

    # Thoát giao diện comment
    async def exit():
        exit = await my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Đóng")]')})
        try:
            exit.click()
            log_message("Đã thoát giao diện comment")
        except Exception:
            log_message("Không tìm được nút thoát", logging.ERROR)
            await go_to_home_page(driver)
            return

    # Tìm nút comment
    comment_button = await scroll_until_element_visible(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Bình luận")]')})
    # Đọc bài viết một tí
    await asyncio.sleep(random.uniform(5,15))
    try:
        comment_button.click()
        await asyncio.sleep(random.uniform(2,5))
    except Exception:
        log_message("Không thể tìm được nút comment", logging.ERROR)
        return

    # Nhập comment
    binhluan = await my_find_element(driver, {("xpath", '//android.widget.AutoCompleteTextView')})
    try:
        # Nhập comment, thay thế bằng hàm input text nếu bị ban, và sửa được hàm input text
        await asyncio.sleep(random.uniform(2,5))
        binhluan.set_text(text)
        await asyncio.sleep(random.uniform(2,5))
    except Exception:
        log_message("Không tìm được ô nhập comment", logging.ERROR)
        await exit()
        return

    # Gửi comment
    send_comment = await my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Gửi")]')})
    try:
        send_comment.click()
        await asyncio.sleep(random.uniform(3,5))
        log_message("Đã comment")
    except Exception:
        log_message("Không tìm được nút gửi", logging.ERROR)
    await exit()
    return

def load_groups(file_path: str = "nhom_tuyen_dung.json"):
    """Đọc dữ liệu nhóm từ file JSON đã lưu."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        log_message(f"Không tìm thấy file '{file_path}'. Hãy chạy get_groups_data_and_save trước.", logging.WARNING)
    except Exception as e:
        log_message(f"Lỗi khi đọc file '{file_path}': {e}", logging.ERROR)
    return None


def get_random_group(file_path: str = "nhom_tuyen_dung.json", only_link: bool = True):
    """Lấy ngẫu nhiên một nhóm từ file JSON đã lưu."""
    data = load_groups(file_path)
    if not data:
        return None

    groups = data.get("groups", [])
    if not groups:
        log_message("Danh sách nhóm rỗng.", logging.WARNING)
        return None

    g = random.choice(groups)
    return g.get("link") if only_link else g

# lướt facebook
async def surf_fb(driver):
    log_message("Lướt tin nhóm tuyển dụng")
    link = get_random_group()
    logging.info(f"Đi đến nhóm: {link}")
    toolfacebook_lib.redirect_to(driver, link)
    try:
        await asyncio.sleep(random.uniform(5,8))
        scroll_count = random.randint(50, 100)

        while scroll_count > 0:
            count = random.randint(1,2)
            await nature_scroll(driver, max_roll=count, isFast=random.choice([True,False]))
            await asyncio.sleep(random.uniform(1,10))
            if scroll_count % 39 == 0:
                await comment_post(driver, text=random.choice(COMMENTS))
                await asyncio.sleep(random.uniform(3,5))
            if scroll_count % 11 == 0:
                await like_post(driver, random.choice(EMOTION))
                await asyncio.sleep(random.uniform(3,5))                                                                                                           
            scroll_count -= 1
        await asyncio.sleep(random.uniform(2,5))
        log_message("Đã hoàn thành lướt facebook")
    except Exception as e:    
        log_message(f"Error {e}", logging.ERROR)

    await go_to_home_page(driver)
