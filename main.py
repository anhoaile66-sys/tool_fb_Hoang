import uiautomator2 as u2
import asyncio
from util import *
from module import *
from tasks import *

DEVICES_LIST = [
    "7HYP4T4XTS4DXKCY",
    "UWJJOJLB85SO7LIZ",
    "2926294610DA007N",
    "7DXCUKKB6DVWDAQO"
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
    sleep_time = 3

    driver.swipe(start_x, start_y, end_x, end_y, duration=duration)
    await asyncio.sleep(sleep_time)

async def run_on_device(device_id):
    try:
        device = load_device_account(device_id)
        if not device:
            log_message(f"Không tìm thấy dữ liệu cho thiết bị {device_id}", logging.WARNING)
            return
        driver = u2.connect_usb(device_id)
        driver.app_start("com.facebook.katana", ".LoginActivity")
        await asyncio.sleep(random.uniform(10,15))

        other_account = [acc for acc in device['accounts'] if acc['name'] != device['current_account']]
        account = random.choice(other_account)
        log_message(f"Đang đăng nhập vào tài khoản {account['name']} trên thiết bị {device_id}")
        await swap_account(driver, account)
        device['current_account'] = account['name']
        update_current_account(device_id, account['name'])
        # tasks nuôi fb
        await fb_natural_task(driver)
        # clear
        await clear_app(driver)
    except Exception as e:
        log_message(f"Lỗi trên thiết bị {device_id}: {e}", logging.ERROR)

# Chạy task trên tất cả các máy
async def run_all_devices():
    tasks = [run_on_device(device_id) for device_id in DEVICES_LIST]
    await asyncio.gather(*tasks)

# Đặt lịch chạy task
async def main():
    while True:
        await run_all_devices()
        log_message("Đợi 20p cho đến khi chạy task tiếp theo")
        await asyncio.sleep(20 * 60)

if __name__ == "__main__":
    asyncio.run(main())