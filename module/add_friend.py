import logging
from util import *
import requests

API_LINK = "https://api.timviec365.vn/api/crm/customer/getNTDByEmpIdToGetPhoneNumber"

# Gọi API lấy tên ntd, kết bạn
async def add_friend(driver, emp_id:str):
    """
    Lấy ntd, kiểm tra xem có thể kết bạn không, nếu không thì tìm ntd khác
    """

    log_message("Bắt đầu kết bạn")
    # Gọi API lấy ntd
    payload = {
        "emp_ids": [int(emp_id)],
        "size": 1,
        "key": "1697a131cb22ea0ab9510d379a8151f1",
        "getFbLink": True
    }

    try:
        response = requests.post(API_LINK, json=payload)
        data=response.json()
        log_message("Lấy được response")
        if emp_id in data['data']:
            fb_link = data['data'][emp_id][0]['link_user_post']
    except Exception:
        log_message("Có lỗi trong khi gọi API", logging.ERROR)

    # Truy cập link trang cá nhân
    redirect_to(driver, fb_link)
    await asyncio.sleep(random.uniform(20,30))

    # Tìm nút kết bạn
    if add_button := my_find_element(driver, {('xpath', '//android.widget.Button[@content-desc="Thêm bạn bè"]')}):
        add_button.click()
        log_message("Đã gửi lời mời kết bạn")
    elif setting := my_find_element(driver, {('xpath', '//android.widget.Button[contains(@content-desc,"Xem cài đặt khác của trang cá nhân")]')}):
        log_message("Không tìm được nút kết bạn", logging.WARNING)
        setting.click()
        log_message("Mở menu để tìm nút kết bạn")
        if add_button := my_find_element(driver, {('xpath', '//android.widget.Button[@content-desc="Thêm bạn bè"]')}):
            add_button.click()
            log_message("Đã gửi lời mời kết bạn")
        else:
            log_message("Không tìm được nút kết bạn", logging.ERROR)
    else:
        log_message("Không thể kết bạn", logging.ERROR)

    await asyncio.sleep(random.uniform(3,6))
    # Về home
    await go_to_home_page(driver)
    return

