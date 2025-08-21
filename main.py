from fb_task import *
from sending_message_and_adding_friend import *

# Tạo task chạy merge giữa fb và zalo
async def make_task(device_id):
    
    try:
        driver = u2.connect_usb(device_id)
        handler = DeviceHandler(driver, device_id)
        handler.connect()

        # while True:
            # zalo tool run
        handler.run()
            # tool fb
            # await run_on_device(driver, device_id)
    except:
        log_message(f"Lỗi trên thiết bị {device_id}", logging.ERROR)

# Chạy task trên tất cả các máy
async def run_all_devices():
    tasks = [
        make_task(device_id) for device_id in DEVICES_LIST
        ]
    await asyncio.gather(*tasks)

# if __name__ == "__main__":
asyncio.run(run_all_devices())