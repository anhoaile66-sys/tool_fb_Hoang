import asyncio
from module.fb_friends import load_facebook_friends_list_advanced
from util import *
from module import *

# Thoát app, xóa cache khi chờ task
async def clear_app(driver):
    driver.press("recent")
    await asyncio.sleep(2)

    size = driver.window_size()
    width, height = size[0], size[1]

    start_x = width / 2
    end_x = start_x
    start_y = height * 0.7
    end_y = height * 0.2
    duration = 0.04

    driver.swipe(start_x, start_y, end_x, end_y, duration=duration)
    await asyncio.sleep(3)
    driver.press("home")
    driver.press("back")

async def fb_natural_task(driver, crm_id:str, account: str):
    actions = [
        ("Xem reels", lambda: watch_reels(driver)), # Đã test oke
        ("Xem story", lambda: watch_story(driver)),
        ("Lướt tin tuyển dụng", lambda: surf_fb(driver)),
        ("Kết bạn", lambda: add_friend(driver, crm_id)),
        ("Thăm tường bạn bè", lambda: load_facebook_friends_list_advanced(driver, driver.serial, True)),
        ("Bình luận thương hiệu", lambda: comment_recruitment_post(driver, account)),
        ("Thăm trang cá nhân", lambda: tham_trang_ca_nhan(driver)),
    ]
    # Random hóa thứ tự các hành động
    random.shuffle(actions)
    for name, action in actions:
        log_message(f"[{DEVICE_LIST_NAME[driver.serial]}] Thực hiện tác vụ: {name}", logging.INFO)
        await action()
        await asyncio.sleep(random.uniform(4,6))
        # Xóa app, xóa cache sau mỗi tác vụ
        await go_to_home_page(driver)

    log_message(f"[{DEVICE_LIST_NAME[driver.serial]}] Hoàn thành 1 chuỗi task")

# Luồng chạy chính của facebook
async def run_on_device_original(driver):
    try:
        device_id = driver.serial

        # await clear_app(driver)
        await asyncio.to_thread(driver.press, "home")
        await asyncio.to_thread(driver.app_start, "com.facebook.katana", ".LoginActivity")
        await asyncio.sleep(random.uniform(10,15))

        device = load_device_account(device_id)

        if device == {}:
            log_message(f"[{DEVICE_LIST_NAME[device_id]}] Không tìm thấy dữ liệu cho thiết bị", logging.WARNING)
            crm_id = "22615833"
            account = "default"
        else:
            crm_id = device['user']['crm_id']
            # Chuyển tài khoản
            # last_time = device['time_logged_in']
            # if (last_time != '0') and (datetime.fromisoformat(last_time) + timedelta(hours=random.randint(4,6))) < datetime.now():
                # Đủ thời gian, chuyển tài khoản
            account_count = device['accountCount']
            current_account_index=0
            for acc in device['accounts']:
                if acc['account'] == device['current_account']:
                    break
                current_account_index+=1
            next_account_index = current_account_index
            check_home_page = True
            while True:
                next_account_index = (next_account_index + 1) % account_count
                next_account = device['accounts'][next_account_index]
                if await swap_account(driver, next_account, check_home_page):
                    device['current_account'] = next_account['account']
                    break
                check_home_page = False
                if next_account_index == current_account_index:
                    log_message(f"[{DEVICE_LIST_NAME[device_id]}] Không thể đăng nhập vào bất kỳ tài khoản nào", logging.ERROR)
                    return
            account = device['current_account']
        # tasks nuôi fb
        await fb_natural_task(driver, crm_id, account)
        # await share_post(driver, text=random.choice(SHARES))
    except Exception as e:
        log_message(f"[{DEVICE_LIST_NAME[driver.serial]}]❌ Lỗi khi chạy luồng Facebook: {type(e).__name__}\n {e}", logging.ERROR)