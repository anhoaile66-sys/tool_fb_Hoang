import asyncio
import pymongo_management
import toolfacebook_lib
import time
import logging
from util import log_message
from lxml import etree

async def post_to_group(driver, command_id, group_link, content, files=None):
    if files:
        for file in files:
            await toolfacebook_lib.push_file_to_device(driver.serial, file)
        driver.app_start("com.miui.gallery")
    toolfacebook_lib.redirect_to(driver, "https://facebook.com/" + group_link)
    await asyncio.sleep(2)
    joined_group = driver(textContains="đã tham gia nhóm")
    if not joined_group.exists:
        log_message(f"{driver.serial} - Đăng bài lên nhóm: Chưa tham gia nhóm {group_link}", logging.WARNING)
        await toolfacebook_lib.back_to_facebook(driver)
        return

    post_button = driver(text="Bạn viết gì đi...")
    if post_button.exists:
        post_button.click()
        time.sleep(2)
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
        log_message(f"{driver.serial} - Đăng bài lên nhóm: Đã đăng bài viết vào nhóm {group_link}", logging.INFO)
    else:
        log_message(f"{driver.serial} - Đăng bài lên nhóm: Không tìm thấy nút Tạo bài viết", logging.WARNING)
    await toolfacebook_lib.back_to_facebook(driver)
    if files:
        for file in files:
            await toolfacebook_lib.delete_file(driver.serial, file)
    await pymongo_management.execute_command(command_id)
    
async def check_post(driver, user_id):
    posts = await pymongo_management.get_unapproved_posts(user_id)
    if len(posts) == 0:
        return
    for post in posts:
        toolfacebook_lib.redirect_to(driver, "https://facebook.com/" + post['group_link'])
        await asyncio.sleep(1)
        driver(description="Bạn").click()
        while toolfacebook_lib.is_screen_changed(driver):
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
            found = False
            for grandparent in grandparents:
                status = "Đang chờ duyệt"
                for child in grandparent.iter():
                    text = child.attrib.get("text", "")
                    if text == post['content']:
                        found = True
                    if text == "Bình luận":
                        status = "Đã đăng thành công"
                if found:
                    break
            if found:
                if post.get('link', "") == "":
                    post_link = toolfacebook_lib.extract_post_link(driver, grandparent)
                else:
                    post_link = post.get('link', "")
                result = await pymongo_management.update_post_status(post['_id'], status, post_link)
                log_message(f"{driver.serial} - {result[0]['message']}", result[1])
                break
            driver.swipe_ext("up", scale=0.8)
    await asyncio.sleep(1)
    await toolfacebook_lib.back_to_facebook(driver)