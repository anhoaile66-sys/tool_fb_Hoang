import random
import asyncio
import os
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging

# Tạo thư mục log nếu chưa có
log_dir = "assets/logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "toolfacebook.log")

# Cấu hình logging chỉ một lần
logger = logging.getLogger("FacebookToolLogger")
logger.setLevel(logging.DEBUG)

# Tránh thêm nhiều handler trùng lặp
if not logger.handlers:
    # Handler ghi log vào file
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Handler in log ra console (terminal)
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    # console_format = logging.Formatter('\033[1;32m%(asctime)s\033[0m - \033[1;34m%(levelname)s\033[0m - %(message)s')
    # console_handler.setFormatter(console_format)
    # logger.addHandler(console_handler)

def log_message(message, level=logging.INFO):
    """Ghi log ra file và terminal với định dạng chuẩn và màu sắc."""
    logger.log(level, message)

    
# Nhập text, đang có lỗi, sửa sau
async def type_text_input(element, text):
    """
    Gõ từng ký tự một vào element với thời gian trễ ngẫu nhiên,
    giúp mô phỏng hành vi nhập liệu của con người.
    """
    # khi ấn vào ô input thì sleep lại 1 tí
    await asyncio.sleep(random.uniform(0.5, 0.8))
    for char in text:
        element.send_keys(char)  # Gõ từng ký tự
        await asyncio.sleep(random.uniform(0.1, 0.4))  # Dừng ngẫu nhiên giữa các lần gõ
    print(f"Đã nhập {text}")


# Tìm element thỏa mãn
def my_find_element(driver, locators, timeout=5):
    wait = WebDriverWait(driver, timeout)
    for locator in locators:
        try:
            element = wait.until(
                EC.presence_of_element_located(locator)
            )
            log_message(f"Tìm thấy element với locator: {locator}")
            return element
        except TimeoutException:
            log_message(f"Không tìm thấy element bằng {locator}", logging.WARNING)
            continue
        except Exception as e:
            log_message(f"Không tìm thấy do lỗi: {type(e).__name__} - {e}", logging.ERROR)
    log_message("Không tìm thấy element trong danh sách locator", logging.ERROR)
    return None

async def nature_scroll(driver, max_roll=1, duration=0.5, isFast=False):
    """
    Mô phỏng thao tác cuộn bằng ngón tay cái.
    """

    try:
        window_size = driver.get_window_size()
        height = window_size["height"]
        width = window_size["width"]

        start_x = width / 2
        end_x = width*3/4
        start_y = int(height * 0.8)
        end_y = int(height * 0.5)
        sleep = 0.5

        pointer = PointerInput(POINTER_TOUCH, "finger")
        actions = ActionBuilder(driver, mouse=pointer)

        if isFast:
            duration = 0.02
            end_y = int(height * 0.2)
            sleep = 3

        for i in range(max_roll):
            actions.pointer_action.move_to_location(start_x, start_y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(duration)
            actions.pointer_action.move_to_location(end_x, end_y)
            actions.pointer_action.release()
            actions.perform()

            await asyncio.sleep(sleep)
            log_message("Đẫ cuộn +1 lần")
        log_message(f"Đã cuộn {max_roll} lần")
        return True
    except Exception as e:
        log_message(f"Không thể cuộn: {type(e).__name__} - {e}", logging.ERROR)
        return False

async def scroll_up(driver, max_roll=1, duration=0.5, isFast=False):
    """
    Mô phỏng thao tác cuộn ngược.
    """
    try:
        window_size = driver.get_window_size()
        height = window_size["height"]
        width = window_size["width"]

        start_x = width / 4
        end_x = width / 2
        start_y = int(height * 0.5)
        end_y = int(height * 0.8)
        sleep = 0.5

        pointer = PointerInput(POINTER_TOUCH, "finger")
        actions = ActionBuilder(driver, mouse=pointer)

        if isFast:
            duration = 0.02
            end_y = int(height * 0.2)
            sleep = 3

        for i in range(max_roll):
            actions.pointer_action.move_to_location(start_x, start_y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(duration)
            actions.pointer_action.move_to_location(end_x, end_y)
            actions.pointer_action.release()
            actions.perform()

            await asyncio.sleep(sleep)
            log_message("Cuộn ngược +1 lần")
        log_message(f"Cuộn ngược {max_roll} lần")
        return True
    except Exception as e:
        log_message(f"Không thể cuộn ngược: {type(e).__name__} - {e}", logging.ERROR)
        return False

# Kéo xuống để tìm element
async def scroll_until_element_visible(driver, locators, max_scrolls=10):    
    """
    Element khi không hiển thị trên view thường sẽ không tìm được, cần kéo xuống để load và tìm lại
    """

    for i in range(max_scrolls):
        element = my_find_element(driver, locators)
        if element != None:
            return element
        await nature_scroll(driver)
    log_message(f"Không tìm thấy element sau {max_scrolls} roll", logging.ERROR)
    return None

# Tìm về đầu trang
async def scroll_to_top_page(driver, max_scrolls=10):
    """
    Trở về đầu trang để tìm các tác vụ khác
    """
    for i in range(max_scrolls):
        element = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Đi tới trang cá nhân"]')})
        if element != None:
            log_message("Đã về đầu trang")
            return element
        await scroll_up(driver, isFast=True)
        await asyncio.sleep(1)
    log_message(f"Không tìm được đầu trang sau {max_scrolls} roll", logging.ERROR)
    return None