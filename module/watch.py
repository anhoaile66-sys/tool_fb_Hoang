import asyncio
import logging
from util import *

# Xem story, còn một role mới cập nhật là ghi chú cũng sẽ lẫn vào story, cần kiểm tra để bỏ qua
async def watch_story(driver, react=0.3, comment=0.05, skip=0.1, back=0.05, duration=60):
    """
    Story mặc định ở trên đầu trang, khi đăng nhập vào sẽ ở trên đầu\n
    Tỉ lệ react mặc định là 30%\n
    Tỉ lệ comment mặc định là 5%\n
    Tỉ lệ skip story là 10%\n
    Tỉ lệ xem lại story trước là 5%\n
    Thời gian gian mặc định là 1p
    """
    log_message("Bắt đầu watch story")
    # Về đầu trang
    top_page = await go_to_home_page(driver)
    if top_page == None:
        log_message("Không ở trang chủ hoặc không thể về trang chủ", logging.ERROR)
        return
    await asyncio.sleep(5)
    # Tìm story
    story_item = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Tin của ")]')})
    if story_item == None:
        log_message("Không thể tìm được story", logging.ERROR)
        return
    story_item.click()
    log_message("Xem story")
    await asyncio.sleep(duration)

    # react, gửi tin nhắn,... sẽ mở rộng sau
    # do somthing stupid

    log_message("Xem story chán rồi, té thôi")

    # Thoát trang story
    await scroll_up(driver, isFast=True)
    log_message("Đã thoát trang story")

# Xem reels
async def watch_reels(driver, duration=120):
    """
    Lướt để tìm reels rồi bấm xem
    """
    log_message("Bắt đầu watch reels")
    # Về đầu trang
    top_page = await go_to_home_page(driver)
    if top_page == None:
        log_message("Không ở trang chủ hoặc không thể về trang chủ", logging.ERROR)
        return
    await asyncio.sleep(5)
    # Tìm Reels
    reel_item = await scroll_until_element_visible(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Xem thước phim")]')})
    if reel_item == None:
        log_message("Không tìm thấy reels", logging.ERROR)
        return
    reel_item.click()
    log_message("Lướt trên mặt nước anh như cơn sóng")
    # Lướt
    time=random.randint(10,20)
    await asyncio.sleep(time)
    while time<duration:
        await nature_scroll(driver, isFast=True)
        log_message("Content nhảm vl, lướt")
        i=random.randint(20,90)
        time+=i
        await asyncio.sleep(i)
    # Lướt xong thì lướt
    back = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Quay lại")]')}, timeout=10)
    if back == None:
        log_message("Không lối thoát muahahaha", logging.ERROR)
        return
    back.click()
    log_message("Thoát về màn hình chính")
