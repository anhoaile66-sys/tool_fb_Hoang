import asyncio
import pymongo_management
import toolfacebook_lib
import logging
from util import log_message
from lxml import etree

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
        driver(text="ĐĂNG").click()
        log_message(f"{driver.serial} - Đăng bài lên tường: Đã đăng bài viết lên tường", logging.INFO)
        await pymongo_management.execute_command(command_id, "Đã thực hiện")
        log_message(f"{driver.serial} - Đăng bài lên tường: Sau 10s sẽ kiểm tra trạng thái bài viết", logging.INFO)
        await asyncio.sleep(10)
        await check_wall_post(driver, user_id)
    else:
        log_message(f"{driver.serial} - Đăng bài lên tường: Không tìm thấy nút Tạo bài viết", logging.WARNING)
        await pymongo_management.execute_command(command_id, "Lỗi: Không tìm thấy nút Tạo bài viết")
    if files:
        for file in files:
            await toolfacebook_lib.delete_file(driver.serial, file)
    

async def check_wall_post(driver, user_id):
    posts = await pymongo_management.get_unapproved_wall_posts(user_id)
    if len(posts) == 0:
        return
    contents = {}
    for post in posts:
        contents[post['content']] = post
    await toolfacebook_lib.back_to_facebook(driver)
    await asyncio.sleep(1)
    driver.xpath('//*[@resource-id="android:id/list"]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').click()
    start_time = asyncio.get_event_loop().time()
    while toolfacebook_lib.is_screen_changed(driver) and asyncio.get_event_loop().time() - start_time < 300:
        xml = driver.dump_hierarchy()
        tree = etree.fromstring(xml.encode("utf-8"))

        # Tìm nút "Thích"
        like_nodes = tree.xpath("//node[@text='Nút Thích. Hãy nhấn đúp và giữ để bày tỏ cảm xúc về bình luận.' or @text='Đã nhấn nút Thích. Nhấn đúp và giữ để thay đổi cảm xúc.']")
        grandparents = []

        for like in like_nodes:
            parent = like.getparent()
            grandparent = parent.getparent() if parent is not None else None

            if grandparent is not None:
                grandparents.append(grandparent)
        for grandparent in grandparents:
            for child in grandparent.iter():
                text = child.attrib.get("text", "")
                if text in contents:
                    post = contents[text]
                    post_link = await toolfacebook_lib.extract_post_link(driver, grandparent)
                    result = await pymongo_management.update_wall_post_status(post['_id'], "Đã đăng thành công", post_link)
                    log_message(f"{driver.serial} - {result[0]['message']}", result[1])
                    contents.pop(text)
        if len(contents) == 0:
            break
        driver.swipe_ext("up", scale=0.8)
    await asyncio.sleep(1)
    await toolfacebook_lib.back_to_facebook(driver)