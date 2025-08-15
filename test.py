import json
import asyncio
import sys
import uiautomator2 as u2


from tool_init_device import get_account_name
from util import *

device_id = "UWJJOJLB85SO7LIZ"

account = {
        "account": "0971335869",
        "password": "timviec365@",
        "name": None,
        "status": True
    }

driver = u2.connect(device_id)
driver.app_start("com.facebook.katana", ".LoginActivity")
log_message(f"Kết nốt với thiết bị {device_id}")


asyncio.run(get_account_name(driver, account))

print(account['name'])
