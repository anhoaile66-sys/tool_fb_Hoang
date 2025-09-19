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
        ("Xem reels", lambda: watch_reels(driver)),
        ("Xem story", lambda: watch_story(driver)),
        ("Lướt fb", lambda: surf_fb(driver)),
        ("Kết bạn", lambda: add_friend(driver, crm_id)),
        ("Thăm tường bạn bè", lambda: load_facebook_friends_list_advanced(driver, driver.serial, True)),
        ("Bình luận thương hiệu", lambda: comment_recruitment_post(driver, account)),
        ("Thăm trang cá nhân", lambda: tham_trang_ca_nhan(driver)),
    ]
    # Random hóa thứ tự các hành động
    random.shuffle(actions)
    for name, action in actions:
        log_message(f"[{driver.serial}] Thực hiện tác vụ: {name}", logging.INFO)
        await action()
        await asyncio.sleep(random.uniform(4,6))
        # Xóa app, xóa cache sau mỗi tác vụ
        await go_to_home_page(driver)

    log_message(f"[{driver.serial}] Hoàn thành 1 chuỗi task")
# Backward compatibility - original function without interrupt
async def run_on_device_original(driver):
    try:
        device_id = driver.serial

        # await clear_app(driver)
        driver.press("home")
        driver.app_start("com.facebook.katana", ".LoginActivity")
        await asyncio.sleep(random.uniform(10,15))

        device = load_device_account(device_id)

        if device == {}:
            log_message(f"[{device_id}] Không tìm thấy dữ liệu cho thiết bị", logging.WARNING)
            crm_id = "22615833"
            account = "default"
        else:
            crm_id = device['user']['crm_id']
            # Chuyển tài khoản
            # last_time = device['time_logged_in']
            # if (last_time != '0') and (datetime.fromisoformat(last_time) + timedelta(hours=random.randint(4,6))) < datetime.now():
                # Đủ thời gian, chuyển tài khoản
            account_count = device['accountCount']
            i=0
            for acc in device['accounts']:
                i+=1
                if acc['account'] == device['current_account']:
                    break
            if i==account_count: i=0
            for acc in device['accounts']:
                if i==0:
                    device['current_account'] = acc['account']
                    this_account = acc
                    break
                i-=1
            log_message(f"[{device_id}] Đang đăng nhập vào tài khoản {this_account['name']}", logging.INFO)
            await swap_account(driver, this_account)
            account = device['current_account']
        # tasks nuôi fb
        await fb_natural_task(driver, crm_id, account)
        # await share_post(driver, text=random.choice(SHARES))
    except Exception as e:
        log_message(f"[{driver.serial}] Lỗi trong quá trình chạy: {type(e).__name__}\n {e}", logging.ERROR)