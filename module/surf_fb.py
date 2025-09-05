import asyncio
import logging
from util import *

EMOTION = [
    "Thích",
    "Yêu thích",
    "Thương thương",
    "Haha",
    "Wow",
    "Buồn",
    "Phẫn nộ"
]

COMMENTS = [
    # Nhóm khen ngợi, tích cực
    "Tuyệt vời quá! 😍🔥",
    "Chuẩn không cần chỉnh! 👍",
    "Xịn xò quá! 💯",
    "Đẹp quá trời luôn! 🌸",
    "Dễ thương ghê! 🥰",
    "Quá đỉnh luôn! 🚀",
    "Thích ghê á! 💖",
    "Hợp gu mình ghê! 😎",
    "Chuẩn bài! ✅",
    "Chất lượng quá! 🌟",

    # Nhóm cảm xúc, reaction
    "Haha, buồn cười quá! 😂",
    "Đáng yêu ghê! 🐻",
    "Cưng xỉu! 😍",
    "Nhìn mà muốn ăn liền! 🍰",
    "Trời ơi, dễ thương quá! 🥹💗",
    "Yêu quá đi! ❤️",
    "Cười đau bụng luôn! 🤣",
    "Xem mà nhớ hồi xưa ghê! 📸",
    "Đỉnh của chóp! 🏆",
    "Xem hoài không chán! 🎯",

    # Nhóm xã giao, tương tác nhẹ
    "Hôm nay thế nào rồi? 🤔",
    "Đang ở đâu đó? 📍",
    "Lâu quá không gặp! 👋",
    "Hợp lý ghê! ✔️",
    "Chuẩn trend luôn! 🔥",
    "Cũng bình thường thôi 😄",
    "Hóng phần tiếp theo! ⏳",
    "Coi ké với nha! 🙌",
    "Đang làm gì đó? 🕒",
    "Like mạnh! ❤️👍"
]

SHARES = [
    # Nhóm kêu gọi hành động
    "Xem ngay kẻo lỡ! 🔥",
    "Không xem là tiếc đó!",
    "Chia sẻ để mọi người cùng biết nhé!",
    "Ai quan tâm thì đọc nha!",
    "Đọc và suy ngẫm 📖",
    "Mọi người nên biết điều này!",
    "Lưu lại để dùng sau! 📌",
    "Ai cũng nên xem ít nhất một lần!",

    # Nhóm bày tỏ cảm xúc
    "Quá hay luôn! 😍",
    "Đọc xong mà nổi da gà! 😱",
    "Cảm động quá! 💖",
    "Không thể tin nổi! 🤯",
    "Hay hơn cả mong đợi!",
    "Nghe mà muốn rớt nước mắt! 😢",

    # Nhóm bắt trend / vui nhộn
    "Bắt trend liền tay! 💃",
    "Hợp mood ghê! 😎",
    "Ai đã xem chưa nè? 🙋",
    "Cười xỉu 🤣",
    "Không share không được! 😂",
    "Xem xong chỉ biết nói: Đỉnh! 🏆"
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
        log_message("Không thể tìm được nút like", logging.ERROR)
        return
    if emotion == "like":
        like_button.click()
        log_message("Đã thả cảm xúc Thích")
        return

    # Chờ menu cảm xúc xuất hiện
    like_button.long_click()
    await asyncio.sleep(random.uniform(1,2))
    
    # Tìm và chọn cảm xúc mong muốn
    emotion_element = my_find_element(driver, {("xpath", f'//com.facebook.feedback.sharedcomponents.reactions.dock.RopeStyleUFIDockView[@content-desc="{emotion}"]')})
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
        exit = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Đóng")]')})
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
    binhluan = my_find_element(driver, {("xpath", '//android.widget.AutoCompleteTextView')})
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
    send_comment = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Gửi")]')})
    try:
        send_comment.click()
        await asyncio.sleep(random.uniform(3,5))
        log_message("Đã comment")
    except Exception:
        log_message("Không tìm được nút gửi", logging.ERROR)
    await exit()
    return

# Share bài viết
async def share_post(driver, text=""):
    """
    Chia sẻ bài viết lụm được đầu tiên về trang cá nhân
    """
    log_message("Bắt đầu chia sẻ")
    # Tìm nút share
    share_button = await scroll_until_element_visible(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Chia sẻ")]')})
    if share_button == None:
        log_message("Không thể tìm được nút share", logging.ERROR)
        return
    share_button.click()
    await asyncio.sleep(random.uniform(1,2))
    # Phải click vào 1 lần nữa mới có thể tìm element
    share_box = my_find_element(driver, {("xpath", '//android.view.ViewGroup[@content-desc="Chia sẻ lên"]')})
    if share_box:
        # Lấy toạ độ và kích thước phần tử
        bounds = share_box.info['bounds']
        x1, y1 = bounds['left'], bounds['top']
        x2, y2 = bounds['right'], bounds['bottom']

        # Tính vị trí click: 40% từ trên xuống
        click_x = (x1 + x2) / 4
        click_y = y1 + (y2 - y1) * 0.4

        # Click vào vị trí đó
        driver.click(click_x, click_y)
    else:
        log_message("Không tìm thấy nút chia sẻ", logging.ERROR)

    if text != "":
        text_box = my_find_element(driver, {("xpath", '//android.widget.AutoCompleteTextView')})
        if text_box == None:
            log_message("Không thể tìm được ô text", logging.ERROR)
            exit = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đóng"]')})
            if exit == None:
                log_message("Không thể tìm được nút đóng\n Bất lực :)))", logging.ERROR)
                return
            exit.click()
            log_message("Chia sẻ thất bại, thoát chia sẻ", logging.ERROR)
            return
        text_box.set_text(text)
        await asyncio.sleep(1)
        log_message(f"Đã nhập nội dung chia sẻ: {text}")
    
    # Tìm nút chia sẻ ngay
    share_now = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Chia sẻ ngay")]'), ('xpath', '//android.view.ViewGroup[@content-desc="Gửi bằng Messenger"]')})
    if share_now == None:
        log_message("Không thể tìm được nút share", logging.ERROR)
        exit = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đóng"]')})
        if exit == None:
            log_message("Không thể tìm được nút đóng\n Bất lực :)))", logging.ERROR)
            return
        exit.click()
        log_message("Chia sẻ thất bại, thoát chia sẻ", logging.ERROR)
        return
    share_now.click()
    log_message("Đã chia sẻ")

# lướt facebook
async def surf_fb(driver):
    log_message("Lướt fb")
    await go_to_home_page(driver)
    await asyncio.sleep(5,7)

    try:
        await asyncio.sleep(random.uniform(5,8))
        scroll_count = random.randint(20, 30)

        while scroll_count > 0:
            count = random.randint(1,2)
            await nature_scroll(driver, max_roll=count, isFast=random.choice([True,False]))
            await asyncio.sleep(random.uniform(1,10))
            if scroll_count % 11 == 0:
                await comment_post(driver, text=random.choice(COMMENTS))
                await asyncio.sleep(random.uniform(3,5))
            if scroll_count % 21 == 0:
                await like_post(driver, random.choice(EMOTION))
                await asyncio.sleep(random.uniform(3,5))
            # if scroll_count % 25 == 0:
            #     i=random.randint(0,1)
            #     if i:
            #         await share_post(driver, text=random.choice(SHARES))
            #         await asyncio.sleep(3,5)
            #     else:
            #         await share_post(driver)
            #         await asyncio.sleep(3,5)
            scroll_count -= 1
        await asyncio.sleep(random.uniform(2,5))
        log_message("Đã hoàn thành lướt facebook")
    except Exception as e:
        log_message(f"Error {e}", logging.ERROR)

    await go_to_home_page(driver)
