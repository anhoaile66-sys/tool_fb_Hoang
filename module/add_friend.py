import asyncio
import logging
from datetime import datetime
from util import *

# Giới hạn số lần kết bạn theo ngày
friend_request_count = 0
friend_request_date = None
MAX_FRIEND_REQUESTS_PER_DAY = 30

# Hàm quản lý đếm số lần kết bạn
def reset_friend_request_counter():
    """Reset counter nếu sang ngày mới"""
    global friend_request_count, friend_request_date
    current_date = datetime.now().date()
    
    if friend_request_date is None or friend_request_date != current_date:
        friend_request_count = 0
        friend_request_date = current_date
        log_message(f"🔄 Reset counter kết bạn cho ngày mới: {current_date}", logging.INFO)
        return True
    return False

def increment_friend_request_counter():
    """Tăng counter số lần kết bạn"""
    global friend_request_count
    friend_request_count += 1
    log_message(f" Đã kết bạn lần thứ {friend_request_count}/{MAX_FRIEND_REQUESTS_PER_DAY} trong ngày", logging.INFO)
    return friend_request_count

def can_send_friend_request():
    """Kiểm tra có thể gửi lời mời kết bạn không"""
    reset_friend_request_counter()
    return friend_request_count < MAX_FRIEND_REQUESTS_PER_DAY


# Tìm nhóm tuyển dụng, kết bạn với user bất kì
async def add_friend(driver):
    """
    Mở menu, vào nhóm, search,
    chọn nhóm bất kỳ, mở danh sách thành viên,
    (chọn user bất kỳ, kết bạn, quay lại)x3
    """

    # Check số lượng request
    # if REQUESTED >= MAX_FRIEND_REQUEST:
    #     log_message("Đã vượt 90 request/ngày, bỏ qua phần kết bạn")
    #     return


    log_message("Bắt đầu kết bạn")
    # Mở menu
    await go_to_home_page(driver)
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
        await asyncio.sleep(6)
        log_message("Mở giao diện nhóm")
    except Exception:
        log_message("Không tìm thấy nhóm", logging.ERROR)
        await go_to_home_page(driver)
        return
    
    # Tìm nút tìm kiếm
    search = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Tìm kiếm nhóm"]')})
    try:
        search.click()
        await asyncio.sleep(3)
        log_message("Mở giao diện tìm kiếm nhóm")
    except Exception:
        log_message("Không tìm thấy nút tìm kiếm nhóm", logging.ERROR)
        await go_to_home_page(driver)
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
        await go_to_home_page(driver)
        return
    
    # Tìm nhóm bất kì: Cuộn xuống ngẫu nhiên, chọn nhóm ngẫu nhiên xuât hiện
    await nature_scroll(driver, max_roll=random.randint(0, 5), isFast=random.choice([True, False]))
    await asyncio.sleep(4)
    group = my_find_elements(driver, {("xpath", '//android.widget.Button[not(contains(@content-desc, "Tham gia"))]')})
    await asyncio.sleep(2)
    try:
        joined_group = group[random.randint(2, len(group) - 1)]
        joined_group.click()
        log_message(f"Đã vào nhóm: ({joined_group.info['contentDescription']})")
        await asyncio.sleep(3)
    except Exception as e:
        log_message("Không tìm thấy nhóm", logging.ERROR)
        log_message(f"Lỗi :{e}", logging.ERROR)
        await go_to_home_page(driver)
        return
    
    # click vào tên nhóm để mở tùy chọn
    group_name = my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "thành viên")]'), ("xpath", '//android.widget.Button[contains(@content-desc, "Nhóm")]')})

    try:
        log_message(f"Tên nhóm: {group_name.info['contentDescription']}")
        group_name.click()
        await asyncio.sleep(6)
        gioi_thieu = my_find_element(driver, {("text", "Giới thiệu")})
        if not gioi_thieu:
            group_name.click()
        log_message("Đã mở tùy chọn")
    except Exception:
        log_message("Không tìm thấy tên nhóm", logging.ERROR)
        await go_to_home_page(driver)
        return
    
    # Kiểm tra xem có box chào mừng linh tinh hiện ra không
    bo_qua = my_find_element(driver, {('xpath', '//*[contains(@content-desc, "iếp tục")]')})
    if bo_qua:
        bo_qua.click()
        await asyncio.sleep(6)

    # Mở xem tất cả thành viên        
    safe_flag = 10
    while (all_members := my_find_element(driver, {("xpath", '//android.view.View[@content-desc="Xem tất cả"]')})) == None:
        if not safe_flag:
            log_message("Không tìm thấy nút xem tất cả thành viên", logging.ERROR)
            await go_to_home_page(driver)
            return
        await nature_scroll(driver, isFast=True)
        safe_flag-=1
    
    all_members.click()
    await asyncio.sleep(6)
    log_message("Đã mở danh sách thành viên")
    # Tìm thành viên để add
    await nature_scroll(driver, max_roll=2, isFast=True)
    members = my_find_elements(driver, {("xpath", '(//android.widget.Button[contains(@content-desc, "Thêm")])')})
    try:
        members[random.randint(0, len(members) - 1)].click()
        await asyncio.sleep(3)
        log_message("Đã gửi lời mời kết bạn")
    except Exception:
        log_message("Không tìm thấy thành viên để kết bạn", logging.ERROR)
        await go_to_home_page(driver)
        return
    
    # # Quay lại danh sách nhóm
    # for _ in range(3):
    #     driver.press("back")
    #     await asyncio.sleep(3)
    # log_message("Đã quay lại danh sách nhóm")
    await go_to_home_page(driver)
    return
    