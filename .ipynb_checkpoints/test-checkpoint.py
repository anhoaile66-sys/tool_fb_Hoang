# import json
# import asyncio
# import sys
# import uiautomator2 as u2


# from tool_init_device import *
# from util import *
# from module import *
# from tasks import *
# from fb_task import *


# # device_id = "7HYP4T4XTS4DXKCY"
# device_id = "UWJJOJLB85SO7LIZ"

# account = {
#         "account": "0971335869",
#         "password": "timviec365@",
#         "name": None,
#         "status": True
#     }

# driver = u2.connect(device_id)
# driver.app_start("com.facebook.katana", ".LoginActivity")
# log_message(f"Kết nốt với thiết bị {device_id}")

# async def main():
#     await clear_app(driver)


# asyncio.run(main())

# # print(random.choice(COMMENTS))


from datetime import datetime,timedelta

# Lấy thời gian hiện tại
current_time = datetime.now()
print(f"Thời gian hiện tại: {current_time}")

# Lấy thời gian dạng string ISO
iso_time = datetime.now().isoformat()
print(f"Thời gian ISO: {iso_time}")

new_time = current_time + timedelta(hours=0.03)
print(f"thoi gian moi: {new_time}")

print(new_time.isoformat() > iso_time)