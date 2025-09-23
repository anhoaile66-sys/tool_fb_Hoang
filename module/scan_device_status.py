import subprocess
from util import *

WINDOW_ADB_PATH = r".\platform-tools\adb.exe"
LINUX_ADB_PATH = "adb"
# LINUX_ADB_PATH = r"./platform-tools/adb.exe"

def scan_connected_devices():
    """
    Quét các thiết bị đang kết nối qua adb, trả về danh sách device_id
    """
    log_message("Đọc danh sách thiết bị kết nối qua ADB")
    try:
        try:
            result = subprocess.run([LINUX_ADB_PATH, "devices"],
                                    capture_output=True,
                                    text=True,
                                    timeout=10,
                                    encoding='utf-8')
        except Exception:
            result = subprocess.run([WINDOW_ADB_PATH, "devices"],
                                    capture_output=True,
                                    text=True,
                                    timeout=10,
                                    encoding='utf-8')

        device_list = []
        # Bỏ dòng đầu tiên
        lines = result.stdout.strip().split('\n')[1:]
        # Lọc dữ liệu
        for line in lines:
            device_id = None
            connect_status = None
            parts = line.split('\t')
            if len(parts) == 2:
                device_id, connect_status = parts
                # log_message(f"Thiết bị: [{device_id}], Trạng thái: {connect_status}")
                if connect_status == "device":
                    device_list.append(device_id)
                    # log_message(f"📱 Thiết bị [{device_id}] đã kết nối và sẵn sàng")
            else:
                log_message(f"Dòng không hợp lệ: {line}", logging.WARNING)
        log_message(f"📱 Lấy thành công {len(device_list)} devices từ ADB")
        return device_list 

    except Exception as e:
        log_message(f"Lỗi khi quét thiết bị: {e}", logging.ERROR)
        return []
    
DEVICE_LIST = scan_connected_devices()