from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.extensions.android.nativekey import AndroidKey
from appium.webdriver.extensions.action_helpers import ActionHelpers
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from my_utils import log_message, my_find_element, type_text_input, scroll_until_element_visible, nature_scroll, scroll_to_top_page, scroll_up
import asyncio
import random
import logging

# Khong su dung ham nay
def login_facebook(driver, account, password):
    """
    Đăng nhập vào ứng dụng Facebook trên Android
    
    """
    # Thao tác đăng nhập
    # Tìm tất cả ô nhập text có thể tương tác
    input_fields = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (AppiumBy.XPATH, '//android.widget.EditText[@clickable="true" and @enabled="true"]')
        )
    )

    input_fields[0].send_keys(account)  # Nhập số điện thoại
    input_fields[1].send_keys(password)  # Nhập mật khẩu
    # Tìm nút đăng nhập và click
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Đăng nhập"]')
        )
    )
    login_button.click()

# Hàm đăng nhập vào tài khoản đã lưu
async def swap_account(driver, name):
    """
    Đăng nhập vào tài khoản facebook đã lưu sẵn
    
    """
    log_message("Bắt đầu đăng nhập vào tài khoản đã lưu")
    await asyncio.sleep(5)
    try:
        account = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH, f'//android.view.View[@content-desc="{name}"]')
            )
        )
        log_message(f"Đăng nhập thành công vào tài khoản {name}")
    except Exception as e:
        log_message(f"Không thể đăng nhập {type(e).__name__} - {e}", logging.ERROR)
        return
    account.click()
    # Đợi vào màn hình chính
    await asyncio.sleep(6)
    
#Tìm kiếm(chưa hoàn thiện)
async def search(driver, text):
    """
    Tìm nút tìm kiếm, nhập text vào ô tìm kiếm và tìm
    
    """
    
    locators = [
        (AppiumBy.ACCESSIBILITY_ID, "Tìm kiếm"),
        (AppiumBy.ACCESSIBILITY_ID, "Tìm kiếm Facebook")
    ]

    search_button = my_find_element(locators, 5)

    search_button[0].click()

    locators_2 = [
        (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm"]')
    ]
    search_bar = my_find_element(locators_2, 5)

    search_bar.click()
    await type_text_input(search_bar, text)
    await asyncio.sleep(3)

    driver.press_keycode(AndroidKey.ENTER)


#Thả cảm xúc vào bài viết
async def like_post(driver, emotion="like"):
    """
    Tìm nút like phía dưới, scroll vào màn hình, nhấn like.\n
    Nhấn giữ để hiện bảng emote, kéo thả vào emote tương ứng:
    'Thích', 'Yêu thích', 'Thương Thương', 'Haha', 'Wow', 'Phẫn nộ'
    """
    log_message("Bắt đầu like post")
    # Tìm nút like
    like_button = await scroll_until_element_visible(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Nút Thích.")]')})
    if like_button == None:
        log_message("Không thể tìm được nút like", logging.ERROR)
        return
    if emotion == "like":
        like_button.click()
        log_message("Đã thả cảm xúc Thích")
        return

    try:
        pointer = PointerInput(POINTER_TOUCH, "finger")
        actions = ActionBuilder(driver, mouse=pointer)
        
        actions.pointer_action.move_to(like_button)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(1)
        actions.perform()
        
        # Chờ menu cảm xúc xuất hiện
        await asyncio.sleep(1)
        
        # Tìm và chọn cảm xúc mong muốn
        emotion_element = my_find_element(driver, {(AppiumBy.XPATH, f'//com.facebook.feedback.sharedcomponents.reactions.dock.RopeStyleUFIDockView[@content-desc="{emotion}"]')})
        emotion_element.click()
        log_message(f"Đã thả cảm xúc {emotion}")
    except Exception as e:
        log_message(f"Không thể thả cảm xúc: {type(e).__name__} - {e}", logging.ERROR)

# Bình luận vào bài viết
async def comment_post(driver, text):
    """
    Tìm nút comment phía dưới, nhấn vào và comment đoạn comment cho trước"""
    log_message("Bắt đầu comment post")
    # Tìm nút comment
    comment_button = await scroll_until_element_visible(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Bình luận")]')})
    if comment_button == None:
        log_message("Không thể tìm được nút comment", logging.ERROR)
        return
    
    comment_button.click()
    # Chờ giao diện comment xuất hiện
    await asyncio.sleep(1)

    # Nhập comment
    binhluan = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.AutoCompleteTextView')})
    if binhluan == None:
        log_message("Không tìm được ô nhập comment", logging.ERROR)
        return
    
    # Nhập comment, thay thế bằng hàm input text nếu bị ban, và sửa được hàm input text
    await asyncio.sleep(2)
    binhluan.send_keys(text)
    await asyncio.sleep(2)

    # Gửi comment
    send_comment = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Gửi")]')})
    if send_comment == None:
        log_message("Không tìm được nút gửi", logging.ERROR)
        return
    send_comment.click()
    log_message("Đã comment")
    
    # Thoát giao diện comment
    exit = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Đóng")]')})
    if exit == None:
        log_message("Không tìm được nút thoát", logging.ERROR)
        return
    exit.click()
    log_message("Đã thoát giao diện comment")


# Share bài viết
async def share_post(driver, text=""):
    """
    Chia sẻ bài viết lụm được đầu tiên về trang cá nhân
    """
    log_message("Bắt đầu chia sẻ")
    # Tìm nút share
    share_button = await scroll_until_element_visible(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Chia sẻ")]')})
    if share_button == None:
        log_message("Không thể tìm được nút share", logging.ERROR)
        return
    share_button.click()
    await asyncio.sleep(1)
    # Phải click vào 1 lần nữa mới có thể tìm element
    pointer = PointerInput(POINTER_TOUCH, "finger")
    actions = ActionBuilder(driver, mouse=pointer)
    
    actions.pointer_action.move_to_location(532, 1791)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.1)
    actions.pointer_action.release()
    actions.perform()
    await asyncio.sleep(1)
    log_message("Click vào để lấy elment")

    if text != "":
        text_box = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.AutoCompleteTextView')})
        if text_box == None:
            log_message("Không thể tìm được ô text", logging.ERROR)
            exit = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Đóng"]')})
            if exit == None:
                log_message("Không thể tìm được nút đóng\n Bất lực :)))", logging.ERROR)
                return
            exit.click()
            log_message("Chia sẻ thất bại, thoát chia sẻ", logging.ERROR)
            return
        text_box.send_keys(text)
        await asyncio.sleep(1)
        log_message(f"Đã nhập nội dung chia sẻ: {text}")
    
    # Tìm nút chia sẻ ngay
    share_now = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Chia sẻ ngay")]')})
    if share_now == None:
        log_message("Không thể tìm được nút share", logging.ERROR)
        exit = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Đóng"]')})
        if exit == None:
            log_message("Không thể tìm được nút đóng\n Bất lực :)))", logging.ERROR)
            return
        exit.click()
        log_message("Chia sẻ thất bại, thoát chia sẻ", logging.ERROR)
        return
    share_now.click()
    log_message("Đã chia sẻ")

# Xem story, còn một role mới cập nhật là ghi chú cũng sẽ lẫn vào story, cần kiểm tra để bỏ qua
async def watch_story(driver, react=0.3, comment=0.05, skip=0.1, back=0.05, duration=60):
    """
    Story mặc định ở trên đầu trang, khi đăng nhập vào sẽ ở trên đầu\n
    Tỉ lệ react mặc định là 30%\n
    Tỉ lệ comment mặc định là 5%\n
    Tỉ lệ skip story là 10%\n
    Tỉ lệ xem lại story trước là 5%\n
    Thời gian gian mặc định là 1p
    """
    log_message("Bắt đầu watch story")
    # Về đầu trang
    top_page = await scroll_to_top_page(driver)
    if top_page == None:
        log_message("Không ở trang chủ hoặc không thể về trang chủ", logging.ERROR)
        return
    await asyncio.sleep(5)
    # Tìm story
    story_item = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Tin của ")]')})
    if story_item == None:
        log_message("Không thể tìm được story", logging.ERROR)
        return
    story_item.click()
    log_message("Xem story")
    await asyncio.sleep(duration)

    # react, gửi tin nhắn,... sẽ mở rộng sau
    # do somthing stupid

    log_message("Xem story chán rồi, té thôi")

    # Thoát trang story
    exit = await scroll_up(driver, isFast=True)
    if exit:
        log_message("Đã thoát trang story")
        return
    log_message("Không lối thoát hẹ hẹ", logging.ERROR)

# Xem reels
async def watch_reels(driver, duration=120):
    """
    Lướt để tìm reels rồi bấm xem
    """
    log_message("Bắt đầu watch reels")
    # Về đầu trang
    top_page = await scroll_to_top_page(driver)
    if top_page == None:
        log_message("Không ở trang chủ hoặc không thể về trang chủ", logging.ERROR)
        return
    await asyncio.sleep(5)
    # Tìm Reels
    reel_item = await scroll_until_element_visible(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Xem thước phim")]')})
    if reel_item == None:
        log_message("Không tìm thấy reels", logging.ERROR)
        return
    reel_item.click()
    log_message("Lướt trên mặt nước anh như cơn sóng")
    # Lướt
    time=random.randint(10,20)
    await asyncio.sleep(time)
    while time<duration:
        await nature_scroll(driver, isFast=True)
        log_message("Content nhảm vl, lướt")
        i=random.randint(20,90)
        time+=i
        await asyncio.sleep(i)
    # Lướt xong thì lướt
    back = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Quay lại")]')}, timeout=10)
    if back == None:
        log_message("Không lối thoát muahahaha", logging.ERROR)
        return
    back.click()
    log_message("Thoát về màn hình chính")


# Tạo bài post mới
async def new_post(driver, text, images={}):
    """
    Tạo bài đăng mới, bài đăng bao gồm text, ảnh(nếu có)

    image: truyền vào {"","",...} tên ảnh/video (không có đuôi định dạng)
    """

    # Hàm tìm nút hủy
    def huy():
        huy = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Hủy"]')})
        if huy == None:
            log_message("Không tìm được nút hủy\n Bất lực", logging.ERROR)
            return
        huy.click()
    # Hàm tìm nút back
    def back():
        back = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Quay lại"]')})
        if back == None:
            log_message("Không tìm được nút quay lại\n Bất lực", logging.ERROR)
            return
        back.click()
    # Hàm tìm nút bỏ bài viết
    def bo():
        bo = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Bỏ bài viết"]')})
        if bo == None:
            log_message("Không tìm được nút bỏ\n Bất lực", logging.ERROR)
            return
        bo.click()

    log_message("Bắt đầu tạo bài đăng mới")
    # Về đầu trang
    top_page = await scroll_to_top_page(driver)
    if top_page == None:
        log_message("Không ở trang chủ hoặc không thể về trang chủ", logging.ERROR)
        return
    await asyncio.sleep(5)

    # Tìm ô tạo bài đăng
    make_post = my_find_element(driver, {(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Viết bài trên Facebook"]')})
    if make_post == None:
        log_message("Không tìm được ô tạo bài đăng", logging.ERROR)
        return
    make_post.click()
    log_message("Vào giao diện tạo bài đăng")
    await asyncio.sleep(1)

    # Nếu có ảnh thì chọn ảnh theo tên
    if images:
        add_image = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Ảnh/video"]')})
        if add_image == None:
            log_message("Không thêm được ảnh")
            back()
            return
        add_image.click()
        log_message("Vào giao diện chọn ảnh")
        await asyncio.sleep(1)

        # Tìm nút thêm nhiều (dù chỉ có 1 ảnh cũng chọn)
        multi_choice = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Chọn nhiều file"]')})
        if multi_choice == None:
            log_message("Không tìm được nút multichoice", logging.ERROR)
            huy()
            back()
            return
        multi_choice.click()
        log_message("Giao diện thêm ảnh")
        await asyncio.sleep(1)

        # Vòng lặp
        first = True
        for image_path in images:
            image = my_find_element(driver, {(AppiumBy.XPATH, f'//android.widget.Button[contains(@content-desc, "{image_path}")]')})
            if image == None:
                log_message(f"Không tìm được hình ảnh: {image_path}", logging.ERROR)
                huy()
                back()
                if not first:
                    bo()
                return
            log_message(f"Tìm được ảnh: {image_path}")
            image.click()
            first = False
        log_message("Đã thêm toàn bộ ảnh")

        # Tìm nút tiếp để chuyển về nhập text
        tiep = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="Tiếp"]')})
        if tiep == None:
            log_message("Không tìm thấy nút tiếp tục", logging.ERROR)
            huy()
            back()
            bo()
            return
        log_message("Trở về nhập text")
        tiep.click()
        await asyncio.sleep(1)

    # Nhập text
    log_message("Về giao diện nhập text")
    text_input = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.AutoCompleteTextView')})
    if text_input == None:
        log_message("Không tìm được ô nhập text", logging.ERROR)
        back()
        if images:
            bo()
        return
    await asyncio.sleep(1)
    text_input.send_keys(text)
    log_message("Nhập xong text")
    await asyncio.sleep(1)

    # Đăng
    dang = my_find_element(driver, {(AppiumBy.XPATH, '//android.widget.Button[@content-desc="ĐĂNG"]')})
    if dang == None:
        log_message("Không tìm được nút đăng", logging.ERROR)
        back()
        if images:
            bo()
        return
    dang.click()
    log_message("Đăng thành công")
async def main():

    options = UiAutomator2Options().load_capabilities({
    "platformName": "Android",  # Bắt buộc: Hệ điều hành Android
    "deviceName": "Android Emulator",  # Tên thiết bị (xem qua `adb devices`)
    "udid": "c7326412",  # ID cụ thể của thiết bị (nếu có nhiều thiết bị)
    "appPackage": "com.facebook.katana",  # Package app Facebook
    "appActivity": ".LoginActivity",  # Màn hình đăng nhập
    "newCommandTimeout": 300, # Tăng thời gian chờ lệnh lên 300s
    "noReset": True,  # Không reset app
    "autoLaunch": False,
    "automationName": "UiAutomator2"
    })

    # Khởi tạo driver
    driver = webdriver.Remote('http://localhost:4723', options=options)

    text = "Trời ơi nó đãaaa"
    account = "0344331495"
    password = "Hhp123456"

    name = "Linh Lê"

    images = {
        "Ảnh chụp vào ngày thg 7 31, 2025 11:36"
    }
    # await search(text)

    # login_facebook(account, password)
    # await swap_account(driver2, name)

    # await like_post(driver)
    # await asyncio.sleep(1)
    # await nature_scroll(driver, max_roll=4)
    # await like_post(driver, "Yêu thích")
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
    await new_post(driver, text, images)

asyncio.run(main())