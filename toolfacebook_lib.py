import asyncio
import re
import cv2
import subprocess
import easyocr
import requests
import aiohttp
import os
import numpy as np

# Truy cập 1 trang facebook qua link
def redirect_to(driver, link):
    driver.shell(f"am start -a android.intent.action.VIEW -d '{link}'")

# Truy cập 1 trang facebook qua link
def redirect_to(driver, link):
    driver.shell(f"am start -a android.intent.action.VIEW -d '{link}'")

# Trở về trang chủ của facebook
async def back_to_facebook(driver):
    driver.press("recent")
    await asyncio.sleep(1)

    size = driver.window_size()
    width, height = size[0], size[1]

    start_x = width / 2
    end_x = start_x
    start_y = height * 0.7
    end_y = height * 0.2
    duration = 0.04

    driver.swipe(start_x, start_y, end_x, end_y, duration=duration)
    await asyncio.sleep(1)
    driver.press("home")
    driver.press("back")
    driver.app_start("com.facebook.katana") 

# Ấn vào ảnh mẫu trên màn hình
async def click_template(driver, template, threshold = 0.8, scale_start = 50, scale_end = 150, scale_step = 10):
    await asyncio.sleep(1)
    screen = await asyncio.to_thread(driver.screenshot, format='opencv')
    template = await asyncio.to_thread(cv2.imread, f"Templates/{template}.png")

    for scale in range(scale_start, scale_end, scale_step):
        # Resize template
        resized = cv2.resize(template, None, fx=scale/100, fy=scale/100, interpolation=cv2.INTER_AREA)
        if resized.shape[0] > screen.shape[0] or resized.shape[1] > screen.shape[1]:
            break

        # Template matching
        result = cv2.matchTemplate(screen, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # Kiểm tra độ khớp
        if max_val > threshold:
            top_left = max_loc
            h, w, _ = resized.shape
            await asyncio.to_thread(driver.click, top_left[0] + w // 2, top_left[1] + h // 2)
            return True
    return False

# Trích xuất số từ chuỗi
def parse_number(s):
    # Tìm tất cả chuỗi gồm các chữ số liền nhau
    numbers = re.findall(r'\d+', s)
    # Chuyển thành mảng số nguyên
    return [int(num) for num in numbers]

# Tải file từ server api
async def download_file_from_server(file_name):
    # URL của ảnh
    url = "https://socket.hungha365.com:4000/uploads/" + file_name

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    # Sử dụng asyncio.to_thread cho file I/O
                    await asyncio.to_thread(_write_file, "Files/" + file_name, content)
                    return "✅ Đã tải file: " + file_name
                else:
                    error_text = await response.text()
                    return "❌ Lỗi khi tải file. Vui lòng thử lại sau: " + error_text
    except Exception as e:
        return f"❌ Lỗi khi tải file: {str(e)}"

def _write_file(filepath, content):
    """Helper function for writing file synchronously"""
    with open(filepath, "wb") as f:
        f.write(content)

# Xóa file đã tải về
async def delete_local_file(file_name):
    try:
        await asyncio.to_thread(subprocess.run, ["del", "Files\\" + file_name], shell=True, check=True)
        return "✅ Đã xóa file: " + file_name
    except subprocess.CalledProcessError:
        return "⚠️ File không tồn tại hoặc không thể xóa: " + file_name
    
# Gửi file đến thiết bị
async def push_file_to_device(device_id, file_name, remote_path="/sdcard/Download/"):
    try:
        await download_file_from_server(file_name)
        await asyncio.to_thread(subprocess.run, ["platform-tools\\adb", "-s", device_id, "push", "Files/" + file_name, remote_path + file_name], check=True)
        await asyncio.to_thread(subprocess.run, [
            "platform-tools\\adb", "-s", device_id,
            "shell", "am", "broadcast",
            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file://{remote_path + file_name}"
        ], check=True)
    except subprocess.CalledProcessError:
        print(f"{device_id} - ❌ Lỗi khi gửi file. Kiểm tra kết nối hoặc đường dẫn.")
    finally:
        await delete_local_file(file_name)

# Xóa file trên thiết bị
async def delete_file(device_id, file_name, remote_path="/sdcard/Download/"):
    try:
        await asyncio.to_thread(subprocess.run, ["platform-tools\\adb", "-s", device_id, "shell", f"rm '{remote_path + file_name}'"], check=True)
        print(f"{device_id} - ✅ Đã xóa file: {remote_path + file_name}")
    except subprocess.CalledProcessError:
        print(f"{device_id} - ⚠️ File không tồn tại hoặc không thể xóa: {remote_path + file_name}")

# Lấy nội dung clipboard
async def get_clipboard_content(driver, app):
    driver.app_start("com.termux")
    driver.send_keys("termux-clipboard-get > /sdcard/Download/clip.txt\n")
    await asyncio.sleep(3)
    driver.app_start(app)
    # Tên file lưu trên máy tính
    local_filename = "clipboard.txt"
    # Đường dẫn file trên thiết bị Android
    remote_path = "/sdcard/Download/clip.txt"

    # Lệnh adb pull
    command = ["platform-tools/adb", "pull", remote_path, local_filename]
    subprocess.run(command, capture_output=True, text=True)

    # Mở file được pull về và đọc nội dung
    with open(local_filename, "r") as file:
        return file.read()

# Lấy liên kết bài viết
async def extract_post_link(driver, post):
    for node in post.iter():
        if node.attrib.get("text") == "Chia sẻ" or node.attrib.get("content-desc") == "Chia sẻ":
            bounds = parse_number(node.attrib.get("bounds"))
            driver.click((bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2)
    await asyncio.sleep(1)
    await click_template(driver, "copy_link")
    return await get_clipboard_content(driver, "com.facebook.katana")

# Lấy liên kết trang cá nhân
async def extract_facebook_user_link(driver):
    button = driver(description="Xem cài đặt khác của trang cá nhân")
    if button.exists(timeout=1):
        button.click()
    await click_template(driver, "copy_profile_link")
    link = await get_clipboard_content(driver, "com.facebook.katana")
    await asyncio.sleep(1)
    driver(resourceId="com.android.systemui:id/back").click()
    await asyncio.sleep(1)
    driver(resourceId="com.android.systemui:id/back").click()
    return link

# Trích xuất thời gian từ ảnh
def extract_time_from_image(image):
    reader = easyocr.Reader(['vi'])  
    results = reader.readtext(image) 

    ocr_texts = [text for _, text, _ in results]

    time_units = ['giờ', 'phút', 'ngày', 'tháng', 'năm']
    for i, word in enumerate(ocr_texts):
        # Trường hợp 1: "23 giờ" là một phần tử duy nhất
        match = re.match(r'(\d+)\s*(giờ|phút|ngày|tháng|năm)', word.lower())
        if match:
            num, unit = match.groups()
            return f"{num} {unit}"

        # Trường hợp 2: "23", "giờ" là hai phần tử liên tiếp
        if word.lower() in time_units and i > 0:
            prev = ocr_texts[i - 1]
            if prev.isdigit():
                return f"{prev} {word.lower()}"
    return None

# Trích xuất thông tin bình luận
async def extract_comment_info(driver, comment_node, raw_comments, links):
    # Trích xuất thông tin từ các nút con
    all_nodes = driver.xpath(comment_node + '//*').all()
    comment = None
    commenter_node = None
    link_nodes = []
    for child in all_nodes:
        info = child.info
        text = info.get("text", "").strip()
        desc = info.get("contentDescription", "").strip()
        className = info.get("className", "")
        
        # Tên người bình luận
        if child.info.get("index") == 1:
            commenter_node = child
        elif "ViewGroup" in className and desc:
            comment = desc
        elif "Button" in className and text:
            if text.startswith("#"):
                continue
            link_nodes.append((child, text))
    if commenter_node is None or comment is None:
        return None
    
    if comment in raw_comments:
        return {"name": raw_comments[comment], "comment": comment}

    # Lấy bounds và cắt ảnh
    bounds_str = driver.xpath(comment_node).get().attrib.get("bounds", "")
    bounds = parse_number(bounds_str)
    screen = driver.screenshot(format='opencv')
    screen = screen[bounds[1]:bounds[3], bounds[0]:bounds[2]]

    # Trích xuất thời gian từ ảnh
    time_texts = extract_time_from_image(screen)

    # Lấy tên và link người bình luận
    if commenter_node.info.get("text", "").strip() in links:
        name = links[commenter_node.info.get("text", "").strip()]
    else:
        commenter_node.click()
        driver(text="Xem trang cá nhân").click()
        link = await extract_facebook_user_link(driver)
        await asyncio.sleep(0.5)
        driver(resourceId="com.android.systemui:id/back").click()
        name = "<a href='" + link + "'>" + commenter_node.info.get("text", "").strip() + "</a>"
        links[commenter_node.info.get("text", "").strip()] = name

    # Lấy tên và link trong comment
    for child, text in link_nodes:
        if text in links:
            link = links[text]
            comment = comment.replace(text, link)
            continue
        child.click()
        link = extract_facebook_user_link(driver)
        comment = comment.replace(text, "<a href='" + link + "'>" + text + "</a>")
        links[text] = "<a href='" + link + "'>" + text + "</a>"
        
    return {
        "name": name,
        "comment": comment,
        "time": time_texts
    }

# Kiểm tra xem màn hình có thay đổi không
def is_screen_changed(driver, threshold=0.99):
    new_screenshot = driver.screenshot(format='opencv')
    if os.path.exists("Screen Shot\\" + driver.serial + ".png"):
        old_screenshot = cv2.imread("Screen Shot\\" + driver.serial + ".png")
        diff = cv2.absdiff(old_screenshot, new_screenshot)
        score = 1 - (np.sum(diff) / (old_screenshot.shape[0] * old_screenshot.shape[1] * 255))
        cv2.imwrite("Screen Shot\\" + driver.serial + ".png", new_screenshot)
        return score < threshold
    else:
        cv2.imwrite("Screen Shot\\" + driver.serial + ".png", new_screenshot)
        return True
    
async def expand_collapse_section(driver):
    while True:
        clicked = False
        buttons = [node for node in driver.xpath("//*").all() if node.info.get("className") == "android.widget.Button"]
        for button in buttons:
            btn_text = button.info.get("text", "") or ""
            btn_description = button.info.get("contentDescription", "") or ""
            if btn_text == "Xem thêm" or "câu trả lời" in btn_description:
                button.click()
                await asyncio.sleep(1)
                clicked = True
                break
        if not clicked:
            break

async def change_comment_display_mode(driver, base_mode="Phù hợp nhất", mode="Mới nhất"):
    if base_mode == mode:
        return
    while True:
        mode_selector = driver(textContains=base_mode)
        if mode_selector.exists:
            break
        driver.swipe_ext("up", scale=0.8)
        await asyncio.sleep(1)
    mode_selector.click()
    driver(descriptionContains=mode).click()
    await asyncio.sleep(1)