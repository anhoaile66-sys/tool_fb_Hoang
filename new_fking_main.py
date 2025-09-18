from util import *
from module import *
import uiautomator2 as u2
import asyncio


async def run_on_one_device(device_id):
    # Chạy trên 1 thiết bị

    # Kết nối thiết bị
    driver = u2.connect_device(device_id)
    log_message(f"[{device_id}]🔗 Đã kết nối")

    # Chạy task nuôi song song với hàm check status

async def make_task_for_all_devices(driver):
    # Tạo task và chia ra cho tất cả các thiết bị
    tasks = [asyncio.create_task(run_on_one_device(device_id)) for device_id in DEVICE_LIST]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(make_task_for_all_devices())
    except KeyboardInterrupt:
        print("[!] Dừng bằng bàn phím (KeyboardInterrupt)")
    except Exception as e:
        log_message(f"Lỗi chạy chính: {e}", logging.ERROR)