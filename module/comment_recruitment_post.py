import pymongo_management
import toolfacebook_lib
import logging
from util import log_message

def comment_recruitment_post(driver, user_id):
    comment = pymongo_management.get_comment(user_id)
    log_message(comment[0]['message'], comment[1])
    if 'comment' in comment[0]:
        comment = comment[0]
        link = comment.get("link")
        comment = comment.get("comment", None)
        toolfacebook_lib.redirect_to(driver, link)
        driver(text="Bình luận").click()
        driver.send_keys(comment, clear=True)
        driver(description="Gửi").click()
        log_message(f"Bình luận thương hiệu: Đã bình luận: {comment}", logging.INFO)
        toolfacebook_lib.back_to_facebook(driver)