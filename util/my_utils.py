import random
import asyncio
from .log import log_message
import logging
    
# Nhập text
async def type_text_input(element, text):
    """
    Gõ từng ký tự một vào element với thời gian trễ ngẫu nhiên,
    giúp mô phỏng hành vi nhập liệu của con người.
    """
    await asyncio.sleep(random.uniform(0.5, 0.8))
    for char in text:
        element.set_text(element.info['text'] + char)
        await asyncio.sleep(random.uniform(0.1, 0.3))
    log_message(f"Đã nhập: {text}")

# Tìm element thỏa mãn
def my_find_element(d, locators):
    for locator in locators:
        method, value = locator
        try:
            if method == "text":
                element = d(text=value)
            elif method == "desc":
                element = d(description=value)
            elif method == "resourceId":
                element = d(resourceId=value)
            elif method == "className":
                element = d(className=value)
            elif method == "xpath":
                element = d.xpath(value)
            else:
                log_message(f"Không hỗ trợ method: {method}", logging.ERROR)
                continue

            if element.exists:
                log_message(f"Tìm thấy element với locator: {locator}")
                return element
            # else:
                # log_message(f"Không tìm thấy element với locator: {locator}", logging.WARNING)
        except Exception as e:
            log_message(f"Lỗi {type(e).__name__}: {e}", logging.ERROR)
    log_message("Không tìm thấy element trong tất cả locators", logging.ERROR)
    return None

# Tìm nhiều element
def my_find_elements(d, locators):
    elements = []
    for locator in locators:
        method, value = locator
        try:
            found = []
            if method == "xpath":
                selector = d.xpath(value)
                if selector.exists:
                    found = selector.all()
            elif method == "text":
                count = d(text=value).count
                found = [d(text=value, instance=i) for i in range(count)]
            elif method == "desc":
                count = d(description=value).count
                found = [d(description=value, instance=i) for i in range(count)]
            elif method == "resourceId":
                count = d(resourceId=value).count
                found = [d(resourceId=value, instance=i) for i in range(count)]
            elif method == "className":
                count = d(className=value).count
                found = [d(className=value, instance=i) for i in range(count)]
            else:
                log_message(f"Không hỗ trợ method: {method}", logging.ERROR)
                continue

            if found:
                # log_message(f"Tìm thấy {len(found)} element với locator: {locator}")
                elements.extend(found)
            # else:
                # log_message(f"Không tìm thấy element với locator: {locator}", logging.WARNING)

        except Exception as e:
            log_message(f"Lỗi {type(e).__name__} khi xử lý locator {locator}: {e}", logging.ERROR)

    if not elements:
        log_message("Không tìm thấy element nào trong tất cả locator", logging.ERROR)
    log_message(f"Đã tìm thấy {len(elements)} element")
    return elements



async def nature_scroll(d, max_roll=1, isFast=False):
    """
    Mô phỏng thao tác cuộn bằng ngón tay cái.
    """
    size = d.window_size()
    width, height = size[0], size[1]

    start_x = width / 2
    end_x = width*3/4
    start_y = height * 0.8
    end_y = height * 0.2
    duration = 0.04 if isFast else 0.2
    sleep_time = 3 if isFast else 1

    for _ in range(max_roll):
        d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        log_message("Đã cuộn +1 lần")
        await asyncio.sleep(sleep_time)
    log_message(f"Đã cuộn {max_roll} lần")

async def scroll_up(d, max_roll=1, isFast=False):
    """
    Mô phỏng thao tác cuộn ngược.
    """
    size = d.window_size()
    width, height = size[0], size[1]

    start_x = width / 4
    end_x = width / 2
    start_y = height * 0.2
    end_y = height * 0.8
    duration = 0.04 if isFast else 0.2
    sleep = 2 if isFast else 0.5

    for _ in range(max_roll):
        d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        log_message("Cuộn ngược +1 lần")
        await asyncio.sleep(sleep)
    log_message(f"Cuộn ngược {max_roll} lần")

# Kéo xuống để tìm element
async def scroll_until_element_visible(driver, locators, max_scrolls=10):    
    """
    Element khi không hiển thị trên view thường sẽ không tìm được, cần kéo xuống để load và tìm lại
    """

    for _ in range(max_scrolls):
        element = my_find_element(driver, locators)
        if element != None:
            return element
        await nature_scroll(driver)
    log_message(f"Không tìm thấy element sau {max_scrolls} roll", logging.ERROR)
    return None

# Tìm về trang chủ
async def go_to_home_page(driver):
    """
    Trở về đầu trang để tìm các tác vụ khác
    """
    log_message("Đang về trang chủ")
    safe_count = 10
    while (element := my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đi tới trang cá nhân"]')})) == None:
        if not safe_count:
            log_message("Không tìm được homepage sau 10 lần thử", logging.ERROR)
            return None
        driver.press("back")
        await asyncio.sleep(1)
        log_message("Không tìm được trang chủ", logging.WARNING)
        safe_count -= 1
    log_message("Đã về trang chủ")
    return element