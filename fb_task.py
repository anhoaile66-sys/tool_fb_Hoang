import asyncio
from util import *
from module import *
from datetime import datetime, timedelta

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
        ("Xem story", lambda: watch_story(driver)),
        ("Lướt fb", lambda: surf_fb(driver)),
        ("Kết bạn", lambda: add_friend(driver, crm_id)),
        # ("Kiểm tra bài đăng", lambda: check_post(driver, account)),
        # ("Kiểm tra nhóm chờ duyệt", lambda: check_unapproved_groups(driver, account)),
        ("Bình luận thương hiệu", lambda: comment_recruitment_post(driver, account)),
        # ("Nhận lệnh từ CRM", lambda: get_commands(driver, account))
    ]

    # Random hóa thứ tự các hành động
    random.shuffle(actions)
    log_message(f"\n\nThực hiện tác vụ: Xem reels\n")

    await watch_reels(driver)
    await asyncio.sleep(random.uniform(4,6))

    for name, action in actions:
        log_message(f"\n\n{driver.serial} Thực hiện tác vụ: {name}\n", logging.INFO)

        await action()
        await asyncio.sleep(random.uniform(4,6))

    log_message("Hoàn thành 1 chuỗi task")

# Backward compatibility - original function without interrupt
async def run_on_device_original(driver):
    try:
        device_id = driver.serial

        # await clear_app(driver)
        driver.press("home")
        driver.app_start("com.facebook.katana", ".LoginActivity")
        await asyncio.sleep(random.uniform(10,15))

        device = load_device_account(device_id)

        account = "default"
        if device == {}:
            log_message(f"Không tìm thấy dữ liệu cho thiết bị {device_id}", logging.WARNING)
            crm_id = "22615833"
            account = "default"
        else:
            crm_id = device['user']['crm_id']
            # Chuyển tài khoản
            # last_time = device['time_logged_in']
            # if (last_time != '0') and (datetime.fromisoformat(last_time) + timedelta(hours=random.randint(4,6))) < datetime.now():
                # Đủ thời gian, chuyển tài khoản
            i=0
            for acc in device['accounts']:
                i+=1
                if acc['account'] == device['current_account']:
                    break
            if i==3: i=0
            for acc in device['accounts']:
                if i==0:
                    device['current_account'] = acc['account']
                    this_account = acc
                    break
                i-=1
            log_message(f"Đang đăng nhập vào tài khoản {this_account['name']} trên thiết bị {device_id}")
            await swap_account(driver, this_account)
            update_current_account(device_id, this_account)
            account = device['current_account']
        # tasks nuôi fb
        await fb_natural_task(driver, crm_id, account)
        # await share_post(driver, text=random.choice(SHARES))
    except Exception as e:
        log_message(f"Lỗi trên thiết bị {device_id}: {e}", logging.ERROR)