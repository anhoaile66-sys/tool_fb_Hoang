import asyncio
import random
from module import *
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


async def surf_fb(driver):
    # lướt facebook
    log_message("Lướt fb")
    await go_to_home_page(driver)
    await asyncio.sleep(5,7)

    try:
        await asyncio.sleep(random.uniform(5,8))
        scroll_count = random.randint(20, 30)

        while scroll_count > 0:
            count = random.randint(1,2)
            await nature_scroll(driver, max_roll=count, isFast=random.choices([True,False]))
            
            if scroll_count % 11 == 0:
                await comment_post(driver, text=random.choices(COMMENTS))
                await asyncio.sleep(random.uniform(3,5))
            if scroll_count % 7 == 0:
                await like_post(driver, random.choices(EMOTION))
                await asyncio.sleep(random.uniform(3,5))
            if scroll_count % 25 == 0:
                i=random.randint(0,1)
                if i:
                    await share_post(driver, text=random.choices(SHARES))
                    await asyncio.sleep(3,5)
                else:
                    await share_post(driver)
                    await asyncio.sleep(3,5)
            scroll_count -= 1
        await asyncio.sleep(random.uniform(2,5))
        log_message("Đã hoàn thành lướt facebook")
    except Exception as e:
        log_message(f"Error {e}", logging.ERROR)


async def fb_natural_task(driver):

    # Danh sách các hành động tự nhiên
    actions = [
        lambda: watch_story(driver),
        lambda: watch_reels(driver),
        lambda: surf_fb(driver),
        lambda: add_3friend(driver),
    ]

    # Random hóa thứ tự các hành động
    random.shuffle(actions)

    for action in actions:
        await action()
        await asyncio.sleep(random.uniform(4,6))

    log_message("Hoàn thành chuỗi task nuôi Facebook tự nhiên")