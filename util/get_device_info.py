import requests
from datetime import datetime

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
        print(f"Lỗi khi gọi API để đọc thiết bị {device_id}: {e}")
        return {}
    except Exception as e:
        print(f"Lỗi không xác định khi đọc thiết bị {device_id}: {e}")
        return {}