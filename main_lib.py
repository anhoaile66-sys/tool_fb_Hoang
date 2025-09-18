from util import *
import subprocess
import json
import os
import glob

async def check_termux_api_installed(driver):
    device_id = driver.serial
    log_message(f"[{device_id}] Kiểm tra cài đặt Termux")
    result = subprocess.run(["platform-tools/adb", "-s", device_id, "shell", "pm", "list", "packages"], capture_output=True, text=True)
    if not "com.termux" in result.stdout:
        log_message(f"[{device_id}] Cài đặt Termux")
        subprocess.run(["platform-tools/adb", "-s", device_id, "install-multiple", "arm64-v8a/base.apk", "arm64-v8a/split_config.arm64_v8a.apk", "arm64-v8a/split_config.vi.apk", "arm64-v8a/split_config.xxhdpi.apk"])
        result = subprocess.run(["platform-tools/adb", "-s", device_id, "shell", "pm", "list", "packages"], capture_output=True, text=True)
        if not "com.termux" in result.stdout:
            subprocess.run(["platform-tools/adb", "-s", device_id, "install-multiple", "armeabi-v7a/base.apk", "armeabi-v7a/split_config.armeabi_v7a.apk", "armeabi-v7a/split_config.vi.apk", "armeabi-v7a/split_config.xhdpi.apk"])
            result = subprocess.run(["platform-tools/adb", "-s", device_id, "shell", "pm", "list", "packages"], capture_output=True, text=True)
            if not "com.termux" in result.stdout:
                log_message(f"[{device_id}] Lỗi cài đặt Termux", logging.ERROR)
                return False
        driver.app_start("com.termux")
        await asyncio.sleep(10)
        driver(resourceId="com.android.permissioncontroller:id/permission_allow_button").click()
        await asyncio.sleep(10)
    driver.app_start("com.termux")
    driver.send_keys("pkg install termux-api\n")
    return True

async def reset_active():
    # Đường dẫn tới thư mục chứa các file JSON
    folder_path = "C:/Zalo_CRM/Zalo_base"

    # Tìm tất cả các file có dạng device_status_*.json
    json_files = glob.glob(os.path.join(folder_path, "device_status_*.json"))

    for file_path in json_files:
        device_id = os.path.basename(file_path).replace("device_status_", "").replace(".json", "")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Nếu có trường 'active', cập nhật thành False
            if 'active' in data:
                data['active'] = False

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            log_message(f"[{device_id}] Lỗi khi đặt lại trạng thái {file_path}: {e}", logging.ERROR)