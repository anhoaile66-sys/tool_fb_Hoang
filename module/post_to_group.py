import asyncio
import pymongo_management
import toolfacebook_lib
import logging
from util import log_message, DEVICE_LIST_NAME

async def post_to_group(driver, command_id, user_id, group_link, content, files=None):
    if files:
        for file in files:
            await toolfacebook_lib.push_file_to_device(driver.serial, file)
        driver.app_start("com.miui.gallery")
    toolfacebook_lib.redirect_to(driver, "https://facebook.com/" + group_link)
    await asyncio.sleep(2)
    joined_group = driver(textContains="đã tham gia nhóm")
    if not joined_group.exists:
        log_message(f"{DEVICE_LIST_NAME[driver.serial]} - Đăng bài lên nhóm: Chưa tham gia nhóm {group_link}", logging.WARNING)
        await toolfacebook_lib.back_to_facebook(driver)
        await pymongo_management.execute_command(command_id, "Lỗi: Chưa tham gia nhóm")
        return

    post_button = driver(text="Bạn viết gì đi...")
    if post_button.exists:
        post_button.click()
        await asyncio.sleep(2)
        width, height = driver.window_size()
        center_x = width // 2
        center_y = height // 2
        driver.click(center_x, center_y)
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
        log_message(f"[{DEVICE_LIST_NAME[driver.serial]}] Đăng bài lên nhóm: Đã đăng bài viết vào nhóm {group_link}", logging.INFO)
        log_message(f"[{DEVICE_LIST_NAME[driver.serial]}] Đăng bài lên nhóm: Đợi 30s để đăng bài viết hoàn tất", logging.INFO)
        await pymongo_management.execute_command(command_id, "Đã thực hiện")
        await asyncio.sleep(30)
    else:
        log_message(f"[{DEVICE_LIST_NAME[driver.serial]}] Đăng bài lên nhóm: Không tìm thấy nút Tạo bài viết", logging.WARNING)
        await pymongo_management.execute_command(command_id, "Lỗi: Không tìm thấy nút Tạo bài viết")
    await toolfacebook_lib.back_to_facebook(driver)
    if files:
        for file in files:
            await toolfacebook_lib.delete_file(driver.serial, file)