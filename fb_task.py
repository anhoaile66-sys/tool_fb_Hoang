import asyncio
from util import *
from module import *
from datetime import datetime, timedelta

DEVICES_LIST = [
    "7HYP4T4XTS4DXKCY",
    "UWJJOJLB85SO7LIZ",
    "2926294610DA007N",
    "7DXCUKKB6DVWDAQO",
    "8HMN4T9575HAQWLN",
    "CEIN4X45I7ZHFEFU",
    "CQIZKJ8P59AY7DHI",
    "EQLNQ8O7EQCQPFXG",
    "MJZDFY896TMJBUPN",
    "TSPNH6GYZLPJBY6X",
    "YH9TSS7XCMPFZHNR",
    "9PAM7DIFW87DOBEU",
    "F6NZ5LRKWWGACYQ8",
    "EM4DYTEITCCYJNFU",
    "EY5H9DJNIVNFH6OR",
    "QK8TEMKZMBYHPV6P",
    "IJP78949G69DKNHM",
    "PN59BMHYPFXCPN8T",
    "EIFYAALRK7U4MRZ9",
    "Z5LVOF4PRGXGTS9H",
    "1ac1d26f0507"
    ]

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

async def get_commands(driver, emp_id):
    commands = pymongo_management.get_commands(emp_id)
    for command in commands:
        if command['type'] == 'post_to_group':
            params = command.get("params", {})
            await post_to_group(driver, command['_id'], params.get("group_link", ""), params.get("content", ""), params.get("files", []))
        if command['type'] == 'join_group':
            params = command.get("params", {})
            await join_group(driver, command['user_id'], params.get("group_link", ""))
        await asyncio.sleep(random.uniform(4, 6))

account = "test"

async def fb_natural_task(driver, emp_id:str):
    actions = [
        ("Xem story", lambda: watch_story(driver)),
        ("Lướt fb", lambda: surf_fb(driver)),
        ("Kết bạn", lambda: add_friend(driver, emp_id)),
        ("Kiểm tra bài đăng", lambda: check_post(driver, account)),
        ("Kiểm tra nhóm chờ duyệt", lambda: check_unapproved_groups(driver, account)),
        ("Nhận lệnh từ CRM", lambda: get_commands(driver, account))
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

async def run_on_device(driver):
    try:
        device_id = driver.serial

        # await clear_app(driver)
        driver.press("home")
        driver.app_start("com.facebook.katana", ".LoginActivity")
        await asyncio.sleep(random.uniform(10,15))

        device = load_device_account(device_id)
        if not device:
            log_message(f"Không tìm thấy dữ liệu cho thiết bị {device_id}", logging.WARNING)
            emp_id = "22615833"
        else:
            emp_id = device['user']['emp_id']
            # Chuyển tài khoản
            last_time = device['time_logged_in']
            if last_time and (datetime.fromisoformat(last_time) + timedelta(hours=random.randint(4,6))) < datetime.now():
                # Đủ thời gian, chuyển tài khoản
                i=0
                for acc in device['accounts']:
                    i+=1
                    if acc['account'] == device['current_account']:
                        break
                if i==3: i=0
                for acc in device['accounts']:
                    if i==0:
                        account=acc
                        break
                    i-=1
                log_message(f"Đang đăng nhập vào tài khoản {account['name']} trên thiết bị {device_id}")
                await swap_account(driver, account)
                device['current_account'] = account['account']
                update_current_account(device_id, account)
        
        # tasks nuôi fb
        await fb_natural_task(driver, emp_id)
        # await share_post(driver, text=random.choice(SHARES))
    except Exception as e:
        log_message(f"Lỗi trên thiết bị {device_id}: {e}", logging.ERROR)

