import asyncio
import logging
from util import *

# Xem story, còn một role mới cập nhật là ghi chú cũng sẽ lẫn vào story, cần kiểm tra để bỏ qua
async def watch_story(driver, duration=random.uniform(60, 90)):
    """
    Story mặc định ở trên đầu trang
    """
    log_message("Bắt đầu watch story")
    # Về đầu trang
    await go_to_home_page(driver)
    await asyncio.sleep(random.uniform(5,7))
    # Tìm story
    story_item = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Tin của ")]')})
    if story_item == None:
        log_message("Không thể tìm được story", logging.ERROR)
        return
    story_item.click()
    log_message("Xem story")

    # Kiểm tra có hiện box xác nhận không
    ok = my_find_element(driver, {("text", "OK")})
    if ok:
        ok.click()
        await asyncio.sleep(random.uniform(3,4))
    await asyncio.sleep(duration)
    # react, gửi tin nhắn,... sẽ mở rộng sau
    # do somthing stupid

    log_message("Xem story chán rồi, té thôi")

    # Thoát trang story
    driver.press("back")
    log_message("Đã thoát trang story")

# Xem reels
async def watch_reels(driver, duration=random.randint(2700,72000)):
    """
    Lướt để tìm reels rồi bấm xem
    """
    log_message("Bắt đầu watch reels")
    # Về đầu trang
    await go_to_home_page(driver)
    await asyncio.sleep(random.uniform(5,7))
    # Tìm Reels
    reel_item = await scroll_until_element_visible(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Xem thước phim")]')})
    if reel_item == None:
        log_message("Không tìm thấy reels", logging.ERROR)
        return
    reel_item.click()
    log_message("Lướt reels")
    # Lướt
    time=random.uniform(10,30)
    await asyncio.sleep(time)
    while time<duration:
        await nature_scroll(driver, isFast=True)
        log_message("Video tiếp theo")
        i=random.uniform(10,30)
        time+=i
        await asyncio.sleep(i)
    # Lướt xong thì lướt
    driver.press("back")
    log_message("Thoát về màn hình chính")
