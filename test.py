import json
import asyncio
import sys
import uiautomator2 as u2


from tool_init_device import *
from util import *
from module import *
from tasks import *
from fb_task import *


# device_id = "7HYP4T4XTS4DXKCY"
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

async def main():
    await clear_app(driver)


asyncio.run(main())

# print(random.choice(COMMENTS))