import pymongo_management
import toolfacebook_lib
from util import log_message
import asyncio

async def comment_recruitment_post(driver, user_id):
    comment = await pymongo_management.get_comment(user_id)
    log_message(f"{driver.serial} - {comment[0]['message']}", comment[1])
    if 'comment' in comment[0]:
        comment = comment[0]
        link = comment.get("link")
        comment = comment.get("comment", None)
        toolfacebook_lib.redirect_to(driver, link)
        await asyncio.sleep(2)
        driver(text="Bình luận").click()
        await asyncio.sleep(2)
        driver.send_keys(comment, clear=True)
        driver(description="Gửi").click()
        await toolfacebook_lib.back_to_facebook(driver)