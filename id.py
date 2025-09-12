import requests
import json
from typing import List, Dict, Optional

# Device API Configuration
ALL_DEVICE_API = "http://192.168.0.116:4000/api/device/getAllDevices"

def get_all_devices_from_api():
    """
    Lấy danh sách tất cả devices từ API
    Returns: List of device objects hoặc None nếu có lỗi
    """
    try:
        response = requests.post(ALL_DEVICE_API, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        devices = data.get("results", [])
        
        print(f"✅ Lấy thành công {len(devices)} devices từ API")
        return devices
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi parse JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
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
