import asyncio
import logging
from util import *

# Hàm đăng xuất
async def log_out(driver):
    """
    Đăng xuất tài khoản khỏi thiết bị
    """

    await go_to_home_page(driver)

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

    safe_flag = 10
    while (log_out := my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng xuất"]')})) == None:
        if not safe_flag:
            log_message("Không tìm được nút đăng xuất sau 10 lần thử",logging.ERROR)
            await go_to_home_page(driver)
            return
        await nature_scroll(driver, isFast=True)
        safe_flag-=1

    log_out.click()
    log_message("Đang đăng xuất")
    # Đợi hiện box lưu
    await asyncio.sleep(6)
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
    await asyncio.sleep(15)
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
    await asyncio.sleep(6)
    # Tắt box quản lý mật khẩu của google
    gg_password = my_find_element(driver, {("text", "Trình quản lý mật khẩu của Google")})
    if gg_password:
        log_message("Tắt trình quản lý mật khẩu")
        driver.press("back")
    await asyncio.sleep(6)
    # Tìm nút đăng nhập, nếu thấy thì mới có thể tìm được ô nhập text
    login_button = my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng nhập"]')})
    if login_button:
        # Tìm tất cả ô nhập text có thể tương tác
        input_fields = my_find_elements(driver, {("className", 'android.widget.EditText')})
        try:
            input_fields[0].set_text(account)  # Nhập số điện thoại
            input_fields[1].set_text(password)  # Nhập mật khẩu
        except Exception:
            log_message("Không tìm được ô text", logging.ERROR)
            return False
        
        login_button.click()
        log_message("Đang đăng nhập")
        await asyncio.sleep(10)
    else:
        log_message("Không tìm được nút login", logging.ERROR)
        return False
    # Kiểm tra có đăng nhập thành công không
    cant_login = my_find_element(driver, {("text", "Không thể đăng nhập")})
    if cant_login:
        log_message("Đăng nhập thất bại do lỗi không thể đăng nhập", logging.ERROR)
        driver.press("back")
        return False
    # Kiểm tra có yêu cầu lưu tài khoản không
    save = my_find_element(driver, {("text", "Lưu")})
    try:
        save.click()
        log_message("Lưu tài khoản")
        await asyncio.sleep(3)
        # Kiểm tra có yêu cầu lưu mật khẩu vào trình quản lý mật khẩu không
        gg_save = my_find_element(driver, {("text", "Trình quản lý mật khẩu của Google")})
        if gg_save:
            tiep = my_find_element(driver, {("text", "Tiếp tục")})
            tiep.click()
            log_message("Đã lưu mk vào tk gg")
            await asyncio.sleep(6)
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
    await asyncio.sleep(20)
    log_message("Đăng nhập thành công")
    return True

# Hàm đăng nhập vào tài khoản đã lưu
async def swap_account(driver, acc):
    """
    Đăng nhập vào tài khoản facebook đã lưu sẵn
    
    """
    name = acc['name']
    password = acc['password']
    # Đăng xuất
    await log_out(driver)

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

