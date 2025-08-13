import uiautomator2 as u2
import asyncio
import os
import json
from util.log import log_message
from module.login import login_facebook

USER_ACCOUNT_FILE = "user_account.json"
DEVICES_FOLDER = "devices"

def ensure_devices_folder():
    if not os.path.exists(DEVICES_FOLDER):
        os.makedirs(DEVICES_FOLDER)

def save_device_json(device):
    device_id = device["device_id"]
    file_path = os.path.join(DEVICES_FOLDER, f"device_{device_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(device, f, indent=4, ensure_ascii=False)
    log_message(f"Đã tạo file {file_path} cho thiết bị {device_id}")

async def init_device(device):
    device_id = device["device_id"]
    driver = u2.connect_usb(device_id)
    driver.app_start("com.facebook.katana", ".LoginActivity")
    await asyncio.sleep(6)
    for acc in device["accounts"]:
        log_message(f"Đang đăng nhập tài khoản {acc.get('name', acc.get('account', '') )} trên thiết bị {device_id}")
        await login_facebook(driver, acc)
        await asyncio.sleep(3)
        device["current_account"] = acc.get("name", acc.get("account", ""))
        save_device_json(device)

async def main():
    ensure_devices_folder()
    with open(USER_ACCOUNT_FILE, "r", encoding="utf-8") as f:
        devices = json.load(f)
    tasks = [init_device(device) for device in devices]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())