import asyncio
import logging
from util import *

# Hàm đăng xuất
async def log_out(driver):
    """
    Đăng xuất tài khoản khỏi thiết bị
    """

    log_message("Đăng xuất")
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
    # Kéo hết xuống dưới
    await nature_scroll(driver, max_roll=2, isFast=True)
    log_message("Tới cuối trang")

    # Tìm nút đăng xuất
    log_out = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng xuất"]')})
    try:
        log_out.click()
        log_message("Đang đăng xuất")
        # Đợi hiện box lưu
        await asyncio.sleep(6)
    except Exception:
        log_message("Không tìm thấy nút đăng xuất", logging.ERROR)
        return
    # Xác nhận lưu tài khoản(nếu có)
    save = my_find_element(driver, {("text", "LƯU")})
    try:
        save.click()
        log_message("Lưu tài khoản")
        await asyncio.sleep(3)
    except Exception:
        log_message("Không thấy box lưu tài khoản", logging.WARNING)
    # Xác nhận đăng xuất
    xac_nhan = my_find_element(driver, {("text", "ĐĂNG XUẤT")})
    try:
        xac_nhan.click()
    except Exception:
        log_message("Không thấy box xác nhận", logging.ERROR)
        return
    # Đợi load trang chọn tài khoản
    await asyncio.sleep(10)
    log_message("Đăng xuất thành công")

# Đăng nhập lần đầu
async def login_facebook(driver, acc):
    """
    Đăng nhập và lưu tài khoản vào ứng dụng Facebook trên Android
    
    """
    # Thao tác đăng nhập
    account = acc['account']
    password = acc['password']

    # Tìm nút chuyển trang cá nhân
    while swap := my_find_element(driver, {("text", "Dùng trang cá nhân khác"), ("text", "Đăng nhập bằng tài khoản khác")}):
        swap.click()
    await asyncio.sleep(15)
    # Tìm tất cả ô nhập text có thể tương tác
    input_fields = my_find_elements(driver, {("className", 'android.widget.EditText')})
    try:
        input_fields[0].set_text(account)  # Nhập số điện thoại
        input_fields[1].set_text(password)  # Nhập mật khẩu
    except Exception as e:
        log_message("Không tìm được ô text")
        return
    # Tìm nút đăng nhập và click
    login_button = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng nhập"]')})
    try:
        login_button.click()
        log_message("Đang đăng nhập")
        await asyncio.sleep(10)
    except Exception:
        log_message("Không tìm được nút login", logging.ERROR)
        return
    
    # Kiểm tra có yêu cầu lưu tài khoản không
    save = my_find_element(driver, {("text", "Lưu")})
    try:
        save.click()
        log_message("Lưu tài khoản")
        await asyncio.sleep(3)
    except Exception:
        log_message("Không thấy box lưu tài khoản", logging.WARNING)
    
    # Kiểm tra có yêu cầu quyền gì không
    while skip := my_find_element(driver, {("text", "Bỏ qua")}):
        skip.click()
        log_message("Bỏ qua")
        await asyncio.sleep(3)
        check_skip = my_find_element(driver, {("text", "BỎ QUA")})
        if check_skip != None:
            check_skip.click()
            await asyncio.sleep(3)

    # Đợi load trang chủ
    await asyncio.sleep(15)
    log_message("Đăng nhập thành công")

# Hàm đăng nhập vào tài khoản đã lưu
async def swap_account(driver, acc):
    """
    Đăng nhập vào tài khoản facebook đã lưu sẵn
    
    """
    name = acc['name']
    password = acc['password']
    # Đăng xuất
    log_out(driver)

    # Đăng nhập
    log_message(f"Bắt đầu đăng nhập vào tài khoản {name}")
    await asyncio.sleep(5)
    account = my_find_element(driver, {("xpath", f'//android.view.View[@content-desc="{name}"]')})
    try:
        account.click()
    except Exception:
        log_message(f"Không thể đăng nhập", logging.ERROR)
        return
    # Tìm xem có bắt nhập mật khẩu lại không
    login = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng nhập"]')})
    if login != None:
        pass_box = my_find_element(driver, {("xpath", 'android.widget.EditText')})
        try:
            pass_box.set_text(password)
            login.click()
            await asyncio.sleep(2)
        except Exception:
            log_message("Không tìm được ô nhập mật khẩu", logging.ERROR)
            return

    # Kiểm tra có yêu cầu lưu tài khoản không
    save = my_find_element(driver, {("text", "Lưu")})
    try:
        save.click()
        log_message("Lưu tài khoản")
        await asyncio.sleep(3)
    except Exception:
        log_message("Không thấy box lưu tài khoản", logging.WARNING)

    # Kiểm tra có yêu cầu quyền gì không
    while skip := my_find_element(driver, {("text", "Bỏ qua")}):
        skip.click()
        log_message("Bỏ qua")
        await asyncio.sleep(3)
        check_skip = my_find_element(driver, {("text", "BỎ QUA")})
        if check_skip != None:
            check_skip.click()
            await asyncio.sleep(3)

    # Đợi vào màn hình chính
    await asyncio.sleep(6)
    log_message(f"Đăng nhập thành công vào tài khoản {name}")

