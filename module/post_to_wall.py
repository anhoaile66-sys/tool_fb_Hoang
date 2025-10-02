import asyncio
import pymongo_management
import toolfacebook_lib
import logging
from util import log_message, DEVICE_LIST_NAME

async def post_to_wall(driver, command_id, user_id, content, files=None):
    if files:
        for file in files:
            await toolfacebook_lib.push_file_to_device(driver.serial, file)
        driver.app_start("com.miui.gallery")
    await toolfacebook_lib.back_to_facebook(driver)
    post_button = driver(text="Viết bài trên Facebook")
    await asyncio.sleep(2)
    if post_button.exists:
        post_button.click()
        await asyncio.sleep(2)
        w, h = driver.window_size()
        driver.click(w // 2, h // 4)
        driver.send_keys(content, clear=True)
    
        if files:
            driver(description="Ảnh/video").click()
            await asyncio.sleep(2)
            driver(description="Chọn nhiều file").click()
            for i in range(len(files)):
                if driver.xpath(f'//android.widget.GridView/android.widget.Button[{i + 1}]/android.widget.Button[1]').exists:
                    driver.xpath(f'//android.widget.GridView/android.widget.Button[{i + 1}]/android.widget.Button[1]').click()
                else:
                    driver.xpath(f'//android.widget.GridView/android.widget.Button[{i + 1}]/android.view.ViewGroup[1]').click()
            driver(text="Tiếp").click()
            await asyncio.sleep(2)
            try:
                driver(scrollable=True).scroll.vert.backward()
            except:
                pass
        await asyncio.sleep(2)
        if driver(description="TIẾP").exists:
            driver(description="TIẾP").click()
        if driver(text="ĐĂNG").exists:
            driver(text="ĐĂNG").click()
        else:
            log_message(f"{DEVICE_LIST_NAME[driver.serial]} - Đăng bài lên tường: Không tìm thấy nút ĐĂNG", logging.WARNING)
            await pymongo_management.execute_command(command_id, "Lỗi: Không tìm thấy nút ĐĂNG")
            return
        log_message(f"{DEVICE_LIST_NAME[driver.serial]} - Đăng bài lên tường: Đã đăng bài viết lên tường", logging.INFO)
        log_message(f"[{DEVICE_LIST_NAME[driver.serial]}] Đăng bài lên tường: Đợi 20s để đăng bài viết hoàn tất", logging.INFO)
        await pymongo_management.execute_command(command_id, "Đã thực hiện")
        await asyncio.sleep(20)
    else:
        log_message(f"{DEVICE_LIST_NAME[driver.serial]} - Đăng bài lên tường: Không tìm thấy nút Tạo bài viết", logging.WARNING)
        await pymongo_management.execute_command(command_id, "Lỗi: Không tìm thấy nút Tạo bài viết")
    if files:
        for file in files:
            await toolfacebook_lib.delete_file(driver.serial, file)