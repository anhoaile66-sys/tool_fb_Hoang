import asyncio
import random
from module import *
from util import *

async def fb_natural_task(driver):
    await swap_account(driver)
    log_message("Đã đăng nhập tài khoản")

    # Danh sách các hành động tự nhiên
    actions = [
        lambda: watch_story(driver),
        lambda: watch_reels(driver),
        lambda: like_post(driver),
        lambda: comment_post(driver),
        lambda: share_post(driver),
        lambda: add_3friend(driver),
    ]

    # Random hóa thứ tự các hành động
    random.shuffle(actions)

    for action in actions:
        await action()
        sleep_time = random.randint(2, 6)
        await asyncio.sleep(sleep_time)

    log_message("Hoàn thành chuỗi task nuôi Facebook tự nhiên")