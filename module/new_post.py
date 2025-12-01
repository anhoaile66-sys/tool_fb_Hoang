import asyncio
import logging
from util import *

# Tạo bài post mới
async def new_post(driver, text, images={}):
    """
    Tạo bài đăng mới, bài đăng bao gồm text, ảnh (nếu có)
    images: danh sách tên ảnh/video (không có đuôi định dạng)
    """

    # === Các hàm phụ ===
    async def huy():
        huy = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Hủy"]')})
        if huy is None:
            log_message("Không tìm được nút hủy\n Bất lực", logging.ERROR)
            return
        huy.click()

    async def back():
        back = await my_find_element(driver, {("xpath", '//android.widget.ImageView[@content-desc="Quay lại"]')})
        if back is None:
            log_message("Không tìm được nút quay lại\n Bất lực", logging.ERROR)
            return
        back.click()

    async def bo():
        bo = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Bỏ bài viết"]')})
        if bo is None:
            log_message("Không tìm được nút bỏ\n Bất lực", logging.ERROR)
            return
        bo.click()

    # === Bắt đầu ===
    log_message("Bắt đầu tạo bài đăng mới")

    # Về đầu trang
    top_page = await go_to_home_page(driver)
    if top_page is None:
        log_message("Không ở trang chủ hoặc không thể về trang chủ", logging.ERROR)
        return
    await asyncio.sleep(2)

    # Tìm ô tạo bài đăng
    selectors = [
    ("xpath", '//android.view.ViewGroup[@content-desc="Viết bài trên Facebook"]'),
    ("xpath", '//android.view.ViewGroup[@content-desc="Bạn đang nghĩ gì?"]'),
    ("xpath", '//android.view.ViewGroup[@content-desc="Bạn đang nghĩ gì thế?"]'),
    ("xpath", '//android.view.ViewGroup[@content-desc="Bạn đang nghĩ gì vậy?"]'),
    ("xpath", '//android.widget.EditText[@text="Bạn đang nghĩ gì?"]'),
    ("textContains", "Bạn đang nghĩ gì"),
    ("textContains", "Viết bài"),
    ("descriptionContains", "Viết bài"),
    ("descriptionContains", "Tạo bài viết"),
    ("descriptionContains", "What's on your mind"),
    ]

    make_post = None
    for selector_type, selector_value in selectors:
        try:
            if selector_type == "xpath":
                make_post = await my_find_element(driver, {("xpath", selector_value)})
            elif selector_type == "textContains":
                make_post = await my_find_element(driver, {("textContains", selector_value)})
            elif selector_type == "descriptionContains":
                make_post = await my_find_element(driver, {("descriptionContains", selector_value)})

            if make_post:
                break
        except Exception:
            continue
    if make_post is None:
        log_message("Không tìm được ô tạo bài đăng", logging.ERROR)
        return
    make_post.click()
    log_message("Vào giao diện tạo bài đăng")
    await asyncio.sleep(1)

    # === Thêm ảnh nếu có ===
    if images:
        add_image = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Ảnh/video"]')})
        if add_image is None:
            log_message("Không thêm được ảnh")
            await back()
            return
        add_image.click()
        log_message("Vào giao diện chọn ảnh")
        await asyncio.sleep(1)

        multi_choice = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Chọn nhiều file"]')})
        if multi_choice is None:
            log_message("Không tìm được nút multichoice", logging.ERROR)
            await huy()
            await back()
            return
        multi_choice.click()
        log_message("Giao diện thêm ảnh")
        await asyncio.sleep(1)

        first = True
        for image_path in images:
            image = await my_find_element(driver, {("xpath", f'//android.widget.Button[contains(@content-desc, "{image_path}")]')})
            if image is None:
                log_message(f"Không tìm được hình ảnh: {image_path}", logging.ERROR)
                await huy()
                await back()
                if not first:
                    await bo()
                return
            log_message(f"Tìm được ảnh: {image_path}")
            image.click()
            first = False
        log_message("Đã thêm toàn bộ ảnh")

        tiep = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="Tiếp"]')})
        if tiep is None:
            log_message("Không tìm thấy nút tiếp tục", logging.ERROR)
            await huy()
            await back()
            await bo()
            return
        log_message("Trở về nhập text")
        tiep.click()
        await asyncio.sleep(1)

    # === Nhập text ===
    log_message("Về giao diện nhập text")
    text_input = await my_find_element(driver, {("xpath", '//android.widget.AutoCompleteTextView')})
    if text_input is None:
        log_message("Không tìm được ô nhập text", logging.ERROR)
        await back()
        if images:
            await bo()
        return
    await asyncio.sleep(1)
    text_input.set_text(text)
    log_message("Nhập xong text")
    await asyncio.sleep(1)

    # === Đăng ===
    dang = await my_find_element(driver, {("xpath", '//android.widget.Button[@content-desc="ĐĂNG"]')})
    if dang is None:
        log_message("Không tìm được nút đăng", logging.ERROR)
        await back()
        if images:
            await bo()
        return
    dang.click()
    log_message("Đăng thành công ✅")
