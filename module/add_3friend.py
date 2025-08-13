import asyncio
import logging
from util import *

# Tìm nhóm tuyển dụng, kết bạn với 3 user bất kì
async def add_3friend(driver):
    """
    Mở menu, vào nhóm, search,
    chọn nhóm bất kỳ, mở danh sách thành viên,
    (chọn user bất kỳ, kết bạn, quay lại)x3
    """
    log_message("Bắt đầu kết bạn")
    # Mở menu
    go_to_home_page(driver)
    menu = my_find_element(driver, {("xpath", '//android.view.View[contains(@content-desc, "Menu")]')})
    try:
        menu.click()
    except Exception:
        log_message("Không tìm được theo xpath, thử tọa độ cứng", logging.WARNING)
        # Cách tồi nhất
        driver.click(661, 202)
    # Đợi chuyển sang tab menu
    await asyncio.sleep(6)
    log_message("Vào menu")

    # Tìm menu "nhóm"
    nhom = my_find_element(driver, {("xpath", '//android.view.ViewGroup[@content-desc="Nhóm"]')})
    try:
        nhom.click()
        await asyncio.sleep(3)
        log_message("Mở giao diện nhóm")
    except Exception:
        log_message("Không tìm thấy nhóm", logging.ERROR)
        go_to_home_page(driver)
        return
    
    # Tìm nút tìm kiếm
    search = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Tìm kiếm nhóm"]')})
    try:
        search.click()
        await asyncio.sleep(3)
        log_message("Mở giao diện tìm kiếm nhóm")
    except Exception:
        log_message("Không tìm thấy nút tìm kiếm nhóm", logging.ERROR)
        go_to_home_page(driver)
        return
    
    # Nhập "tuyển dụng"
    input_search = my_find_element(driver, {("className", "android.widget.EditText")})
    try:
        input_search.set_text("tuyển dụng")
        await asyncio.sleep(3)
        log_message("Đã nhập từ khóa tìm kiếm")
        driver.press("enter")
        await asyncio.sleep(3)
    except Exception:
        log_message("Không tìm thấy ô nhập từ khóa", logging.ERROR)
        go_to_home_page(driver)
        return
    
    # Lặp 3 lần
    for _ in range(3):
        # Tìm nhóm bất kì: Cuộn xuống ngẫu nhiên, chọn nhóm ngẫu nhiên xuât hiện
        nature_scroll(driver, max_roll=random.randint(0, 5, isFast=random.choice([True, False])))
        group = my_find_elements(driver, {("className", 'android.widget.Button')})
        try:
            group[random.randint(0, len(group) - 1)].click()
            await asyncio.sleep(3)
            log_message("Đã vào nhóm")
        except Exception:
            log_message("Không tìm thấy nhóm", logging.ERROR)
            go_to_home_page(driver)
            return
        
        # click vào tên nhóm để mở tùy chọn
        group_name = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "thành viên")]')})
        try:
            group_name.click()
            await asyncio.sleep(3)
            log_message("Đã mở danh sách thành viên")
        except Exception:
            log_message("Không tìm thấy tên nhóm", logging.ERROR)
            go_to_home_page(driver)
            return
        
        # Mở xem tất cả thành viên
        all_members = my_find_element(driver, {("xpath", '//android.view.View[@content-desc="Xem tất cả"]')})
        try:
            all_members.click()
            await asyncio.sleep(3)
            log_message("Đã mở danh sách thành viên")
        except Exception:
            log_message("Không tìm thấy nút xem tất cả thành viên", logging.ERROR)
            go_to_home_page(driver)
            return
        
        # Tìm thành viên để add
        nature_scroll(driver, max_roll=2, isFast=True)
        members = my_find_elements(driver, {("xpath", '(//android.widget.Button[contains(@content-desc, "Thêm")])')})
        try:
            members[random.randint(0, len(members) - 1)].click()
            await asyncio.sleep(3)
            log_message("Đã gửi lời mời kết bạn")
        except Exception:
            log_message("Không tìm thấy thành viên để kết bạn", logging.ERROR)
            go_to_home_page(driver)
            return
        
        # Quay lại danh sách nhóm
        for _ in range(3):
            driver.back()
            await asyncio.sleep(3)
        log_message("Đã quay lại danh sách nhóm")

    