import json

device_status_path = "D:/Zalo_CRM/Zalo_base/device_status_CEIN4X45I7ZHFEFU.json"
with open(device_status_path, 'r', encoding='utf-8') as f:
    device_status = json.load(f)
if device_status.get('active', False):
    print("Device is not active")
