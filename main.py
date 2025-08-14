import uiautomator2 as u2
import asyncio
import os
from util import *
from module import *
from tasks import fb_natural_task

async def run_on_device(device_id):
    try:
        device = load_device_account(device_id)
        if not device:
            log_message(f"Không tìm thấy dữ liệu cho thiết bị {device_id}")
            return
        driver = u2.connect_usb(device_id)
        driver.app_start("com.facebook.katana", ".LoginActivity")
        await asyncio.sleep(6)
        for account in device['acounts']:
            log_message(f"Đang đăng nhập vào tài khoản {account['name']} trên thiết bị {device_id}")
            await swap_account(driver, account)
            update_current_account(device_id, account['name'])
        await fb_natural_task(driver)
    except Exception as e:
        log_message(f"Lỗi trên thiết bị {device_id}: {e}")

async def main():
    device_ids = [f for f in os.listdir("devices") if f.startswith("device_") and f.endswith(".json")]
    device_ids = [f.replace("device_", "").replace(".json", "") for f in device_ids]
    tasks = [run_on_device(device_id) for device_id in device_ids]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())