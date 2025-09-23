import asyncio
import logging
from util import *
import pymongo_management

# Hàm đăng xuất
async def log_out(driver):
    """
    Đăng xuất tài khoản khỏi thiết bị
    """

    await go_to_home_page(driver)

    log_message(f"[{driver.serial}] Đăng xuất")
    menu = await my_find_element(driver, {("xpath", '//*[contains(@content-desc, "Menu")]')})
    try:
        menu.click()
    except Exception:
        log_message(f"[{driver.serial}] Không tìm được nút menu", logging.ERROR)
        return
    # Đợi chuyển sang tab menu
    log_message(f"[{driver.serial}] Trạng thái: Menu")

    safe_flag = 20
    log_out = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng xuất"]')}, safe_flag, True)
    if log_out == None:
        log_message(f"[{driver.serial}] Không tìm được nút đăng xuất sau {safe_flag} lần thử",logging.ERROR)
        await go_to_home_page(driver)
        return
    log_out.click()
    log_message(f"[{driver.serial}] Đang đăng xuất")

    # Xác nhận lưu tài khoản(nếu có)
    save = await my_find_element(driver, {("text", "LƯU")}, 6)
    if save:
        save.click()
        log_message(f"[{driver.serial}] Đã lưu tài khoản")

    # Xác nhận đăng xuất
    xac_nhan = await my_find_element(driver, {("text", "ĐĂNG XUẤT")}, 10)   
    if xac_nhan == None:
        log_message(f"[{driver.serial}] Không tìm thấy box xác nhận đăng xuất", logging.ERROR)
        return
    else:
        xac_nhan.click()
    # Đợi load trang chọn tài khoản
    log_message(f"[{driver.serial}] Đăng xuất thành công")
    await pymongo_management.update_statusFB(driver.serial, "Offline")

# Đăng nhập lần đầu
async def login_facebook(driver, acc):
    """
    Đăng nhập và lưu tài khoản vào ứng dụng Facebook trên Android
    
    """
    # Thao tác đăng nhập
    account = acc['account']
    password = acc['password']

    # Tìm nút chuyển trang cá nhân
    while swap := await my_find_element(driver, {("text", "Dùng trang cá nhân khác"), ("text", "Đăng nhập bằng tài khoản khác")}):
        swap.click()
    await asyncio.sleep(6)
    # Tắt box quản lý mật khẩu của google
    gg_password = await my_find_element(driver, {("text", "Trình quản lý mật khẩu của Google")})
    if gg_password:
        log_message("Tắt trình quản lý mật khẩu")
        driver.press("back")
    await asyncio.sleep(6)
    # Tìm nút đăng nhập, nếu thấy thì mới có thể tìm được ô nhập text
    login_button = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng nhập"]')})
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
    cant_login = await my_find_element(driver, {("text", "Không thể đăng nhập")})
    if cant_login:
        log_message("Đăng nhập thất bại do lỗi không thể đăng nhập", logging.ERROR)
        driver.press("back")
        return False
    # Kiểm tra có yêu cầu lưu tài khoản không
    save = await my_find_element(driver, {("text", "Lưu")})
    try:
        save.click()
        log_message("Lưu tài khoản")
        await asyncio.sleep(3)
        # Kiểm tra có yêu cầu lưu mật khẩu vào trình quản lý mật khẩu không
        gg_save = await my_find_element(driver, {("text", "Trình quản lý mật khẩu của Google")})
        if gg_save:
            tiep = await my_find_element(driver, {("text", "Tiếp tục")})
            tiep.click()
            log_message("Đã lưu mk vào tk gg")
            await asyncio.sleep(6)
    except Exception:
        log_message("Không thấy box lưu tài khoản", logging.WARNING)
    
    # Kiểm tra có yêu cầu quyền gì không
    while skip := await my_find_element(driver, {("text", "Bỏ qua")}):
        skip.click()
        log_message("Bỏ qua")
        await asyncio.sleep(3)
        check_skip = await my_find_element(driver, {("text", "BỎ QUA")})
        if check_skip != None:
            check_skip.click()
            await asyncio.sleep(3)

    # Đợi load trang chủ
    await asyncio.sleep(20)
    log_message("Đăng nhập thành công")
    await pymongo_management.update_statusFB(account, "Online")
    return True

async def check_logged_in(driver):
    """
    Kiểm tra trạng thái đăng nhập của tài khoản trên thiết bị
    
    """
    # Mở ứng dụng Facebook
    driver.app_start("com.facebook.katana")
    home = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đi tới trang cá nhân"]')}, 10, back_if_not_found=True)
    if home is not None:
        return True
    else:
        return False
# Hàm đăng nhập vào tài khoản đã lưu
async def swap_account(driver, acc):
    """
    Đăng nhập vào tài khoản facebook đã lưu sẵn
    
    """
    # Mở ứng dụng Facebook
    driver.app_start("com.facebook.katana")

    # Lấy thông tin tài khoản
    name = acc['name']
    username = acc['account']
    password = acc['password']

    # Đăng xuất nếu đã đăng nhập
    if await check_logged_in(driver):
        await log_out(driver)
    else:
        help_button = await my_find_element(driver, {("text", "Trợ giúp")}, 3)
        if help_button:
            help_button.click()
            await asyncio.sleep(3)
            log_out_btn = await my_find_element(driver, {("xpath", '//*[@content-desc[contains(., "Đăng xuất")]]')})
            log_out_btn.click()
            (await my_find_element(driver, {("text", "ĐĂNG XUẤT")})).click()

    # Đăng nhập
    log_message(f"[{driver.serial}] Bắt đầu đăng nhập vào tài khoản {name}")
    account = await my_find_element(driver, {("xpath", f'//android.view.View[@content-desc="{name}"]')}, 20)
    try:
        account.click()
    except Exception:
        log_message(f"[{driver.serial}] Không thể đăng nhập", logging.ERROR)
        return
    # Tìm xem có bắt nhập mật khẩu lại không
    login = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Đăng nhập"]')})
    if login != None:
        await asyncio.sleep(3)
        driver.send_keys(password)
        login.click()

    # Kiểm tra có yêu cầu lưu tài khoản không
    save = await my_find_element(driver, {("text", "Lưu")})
    try:
        save.click()
        log_message(f"[{driver.serial}] Đã lưu tài khoản")
        await asyncio.sleep(3)
    except Exception:
        pass

    # Kiểm tra có yêu cầu quyền gì không
    while True:
        skip = await my_find_element(driver, {("text", "Bỏ qua")}, 5)
        if skip is not None:
            skip.click()
        else:
            break
    

    # Đợi vào màn hình chính
    if await check_logged_in(driver):
        log_message(f"[{driver.serial}] Đăng nhập thành công vào tài khoản {name}")
        await pymongo_management.update_statusFB(username, "Online")
        return True
    else:
        log_message(f"[{driver.serial}] Đăng nhập thất bại vào tài khoản {name}", logging.ERROR)
        await pymongo_management.update_statusFB(username, "Crash")
        return False