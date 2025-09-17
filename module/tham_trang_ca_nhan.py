import asyncio
import logging
import random
from util import *

EMOTION = [
    "Thích",
    "Yêu thích",
    "Thương thương",
    "Haha",
    "Wow",
    "Buồn",
]

#Thả cảm xúc vào bài viết (Phẫn nộ sẽ đổi thành Buồn, "đấy là tính năng")
async def like_post(driver, emotion="like"):
    """
    Tìm nút like phía dưới, scroll vào màn hình, nhấn like.\n
    Nhấn giữ để hiện bảng emote, kéo thả vào emote tương ứng:
    'Thích', 'Yêu thích', 'Thương Thương', 'Haha', 'Wow', 'Buồn', 'Phẫn nộ'
    """
    log_message(f"[{driver.serial}] Bắt đầu like post")
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

# lướt facebook
async def tham_trang_ca_nhan(driver):
    profile_locators = [
        ("desc", "Đi tới trang cá nhân"),
        ("desc", "Go to profile"),
        ("desc", "Your profile"),
        ("desc", "Trang cá nhân của bạn"),
        ("text", "Đi tới trang cá nhân"),
        ("text", "Go to profile"),
    ]
        
    profile_element = await my_find_element(driver, profile_locators)
        
    if not profile_element:
        print("❌ Không tìm thấy nút 'Đi tới trang cá nhân'")
        return "unknown_user"
        
    profile_element.click()
    print("✅ Đã click vào trang cá nhân")
    await asyncio.sleep(4)
    try:
        await asyncio.sleep(random.uniform(5,8))
        scroll_count = random.randint(5, 20)

        while scroll_count > 0:
            count = random.randint(1,2)
            await nature_scroll(driver, max_roll=count, isFast=random.choice([True,False]))
            await asyncio.sleep(random.uniform(1,10))
            if scroll_count % 7 == 0:
                await like_post(driver, random.choice(EMOTION))
                await asyncio.sleep(random.uniform(3,5))                                                                                                           
            scroll_count -= 1
        await asyncio.sleep(random.uniform(2,5))
        log_message(f"[{driver.serial}] Đã hoàn thành lướt facebook")
    except Exception as e:    
        log_message(f"[{driver.serial}] Error {e}", logging.ERROR)

    await go_to_home_page(driver)
