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

def update_current_account(device_id, account):
    """
    Cập nhật current_account cho thiết bị qua API.
    """
    try:
        url = f"{API_BASE_URL}/device-id/{device_id}"
        payload = {
            "current_account": account['account'],
            "time_logged_in": datetime.now().isoformat()
        }
        
        response = requests.patch(url, json=payload, timeout=10)
        response.raise_for_status()
        
        print(f"Đã cập nhật current_account cho {device_id} → {account['account']}: {account['name']}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API để cập nhật thiết bị {device_id}: {e}")
        return False
    except Exception as e:
        print(f"Lỗi không xác định khi cập nhật thiết bị {device_id}: {e}")
        return False