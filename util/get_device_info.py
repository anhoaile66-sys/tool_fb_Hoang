import requests
import json
from util.log import log_message
import logging

API_BASE_URL = "https://socket.hungha365.com:4000/api/device"

def load_device_account(device_id):
    """
    Đọc thông tin thiết bị từ API, trả về dict tài khoản của thiết bị đó.
    """
    try:
        url = f"{API_BASE_URL}/filter"
        payload = {"device_id": device_id}
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        device_data = response.json()
        
        results = device_data['results']
        if results and len(results) > 0:
            return results[0]
        else:
            return {}
        
    except requests.exceptions.RequestException as e:
        log_message(f"Lỗi khi gọi API để đọc thiết bị {device_id}: {e}", logging.ERROR)
        return {}
    except Exception as e:
        log_message(f"Lỗi không xác định khi đọc thiết bị {device_id}: {e}", logging.ERROR)
        return {}

def get_all_devices_from_api():
    """
    Lấy danh sách tất cả devices từ API
    Returns: List of device objects hoặc None nếu có lỗi
    """
    try:
        url = f"{API_BASE_URL}/getAllDevices"
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        devices = data.get("results", [])
        
        log_message(f"✅ Lấy thành công {len(devices)} devices từ API")
        return devices
        
    except requests.exceptions.RequestException as e:
        log_message(f"❌ Lỗi kết nối API: {e}", logging.ERROR)
        return None
    except json.JSONDecodeError as e:
        log_message(f"❌ Lỗi parse JSON: {e}", logging.ERROR)
        return None
    except Exception as e:
        log_message(f"❌ Lỗi không xác định: {e}", logging.ERROR)
        return None

def get_device():
    """
    Lấy dictionary mapping device_id -> device_name
    Args:
        use_cache: Sử dụng cache hay gọi API mới
    Returns: Dict {device_id: device_name}
    """

    # Gọi API lấy devices
    devices = get_all_devices_from_api()
    
    if devices is None:
        return []
    
    # Tạo dictionary mapping
    device_list = []
    for device in devices:
        device_list.append(device.get("device_id"))
    return device_list

DEVICE_LIST = get_device()

