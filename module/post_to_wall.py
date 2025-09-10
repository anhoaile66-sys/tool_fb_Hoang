import asyncio
import pymongo_management
import toolfacebook_lib
import logging
from util import log_message

async def post_to_wall(driver, command_id, content, files=None):
    if files:
        for file in files:
            await toolfacebook_lib.push_file_to_device(driver.serial, file)
        driver.app_start("com.miui.gallery")
    toolfacebook_lib.back_to_facebook(driver)
    post_button = driver(text="Viết bài trên Facebook")
    if post_button.exists(timeout=2):
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
                driver.xpath(f'//android.widget.GridView/android.widget.Button[{i + 1}]/android.widget.Button[1]').click()
            driver(text="Tiếp").click()
            await asyncio.sleep(2)
            try:
                driver(scrollable=True).scroll.vert.backward()
            except:
                pass
        driver(text="ĐĂNG").click()
        log_message(f"{driver.serial} - Đăng bài lên tường: Đã đăng bài viết lên tường", logging.INFO)
    else:
        log_message(f"{driver.serial} - Đăng bài lên tường: Không tìm thấy nút Tạo bài viết", logging.WARNING)
    if files:
        for file in files:
            await toolfacebook_lib.delete_file(driver.serial, file)
    await pymongo_management.execute_command(command_id)