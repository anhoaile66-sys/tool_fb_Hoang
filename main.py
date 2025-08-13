import uiautomator2 as u2
import asyncio
from util import *
from module import *

# main
async def main():

    # Khởi tạo driver
    # driver = webdriver.Remote('http://localhost:4723', options=options)

    # Khởi tạo driver theo kiểu ui2

    # Khởi động app

    # text = "Trời ơi nó đãaaa"

    # images = {
    #     "Ảnh chụp vào ngày thg 7 31, 2025 11:36"
    # }
    # await search(text)
    # await asyncio.sleep(6)
    
    account_data = load_accounts_from_json("user_account.json")
    device = account_data[0]
    driver = u2.connect_usb(device['device_id'])
    account = device['accounts'][2]
    driver.app_start("com.facebook.katana", ".LoginActivity")
    await asyncio.sleep(6)
    if device['current_account'] != account['name']:
        log_message(f"Đang đăng nhập vào tài khoản {account['name']} trên thiết bị {device['device_id']}")
        await swap_account(driver, account)
        update_current_account("user_account.json", device['device_id'], account['name'])
    # cur_device = ""
    # for account in account_data:
    #     device = account['device_id']
    #     if device == "":
    #         break
    #     if device != cur_device:
    #         cur_device = device
    #         driver = u2.connect_usb(device)
    #         driver.app_start("com.facebook.katana", ".LoginActivity")
    #         await asyncio.sleep(6)
    #     else:
    #         await log_out(driver)
    #     await login_facebook(driver, account)



    # driver.click(1314,350)

    # await swap_account(driver, acc_list[2])
    # my_find_element(driver, {("xpath", '//android.widget.Button[contains(@content-desc, "Tin của ")]')})
    # await nature_scroll(driver)
    # await nature_scroll(driver, isFast=True)
    # await nature_scroll(driver, isFast=True)
    # await scroll_up(driver)
    # await scroll_up(driver, isFast=True)
    # await scroll_to_top_page(driver)
    # await like_post(driver)
    # await asyncio.sleep(1)
    # await nature_scroll(driver, max_roll=4)
    # await like_post(driver, "Yêu thích")
    # await like_post(driver, "Phẫn nộ")

    # await asyncio.sleep(1)
    # await nature_scroll(driver, max_roll=2)
    # await comment_post(driver, "ultr")
    # await asyncio.sleep(1)
    # await nature_scroll(driver, max_roll=3)
    # await share_post(driver, "Muốn làm vợ rồi")
    # await asyncio.sleep(1)
    # await nature_scroll(driver, isFast=True)
    # await asyncio.sleep(10)
    # await watch_story(driver, duration=15)
    # await asyncio.sleep(10)
    # await watch_reels(driver, duration=30)
    # await new_post(driver, text, images)

asyncio.run(main())