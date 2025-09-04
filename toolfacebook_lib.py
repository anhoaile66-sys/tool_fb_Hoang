import time
import re
import cv2
import subprocess
import easyocr
import requests

# Truy cập 1 trang facebook qua link
def redirect_to(driver, link):
    driver.shell(f"am start -a android.intent.action.VIEW -d '{link}'")

# Trở về trang chủ của facebook
def back_to_facebook(driver):
    while not (home_tab := driver(resourceId="com.facebook.katana:id/(name removed)", descriptionContains="Trang chủ")).exists(timeout=1):
        driver(resourceId="com.android.systemui:id/back").click()
    time.sleep(1)
    home_tab.click()

# Ấn vào ảnh mẫu trên màn hình
def click_template(driver, template, threshold = 0.8, scale_start = 50, scale_end = 150, scale_step = 10):
    time.sleep(1)
    screen = driver.screenshot(format='opencv')
    template = cv2.imread(f"Templates/{template}.png")

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
            driver.click(top_left[0] + w // 2, top_left[1] + h // 2)
            return True
    return False

# Trích xuất số từ chuỗi
def parse_number(s):
    # Tìm tất cả chuỗi gồm các chữ số liền nhau
    numbers = re.findall(r'\d+', s)
    # Chuyển thành mảng số nguyên
    return [int(num) for num in numbers]

# Tải file từ server api
def download_file_from_server(file_name):
    # URL của ảnh
    url = "https://socket.hungha365.com:4000/uploads/" + file_name

    # Gửi yêu cầu GET để lấy nội dung ảnh
    response = requests.get(url)

    # Kiểm tra nếu yêu cầu thành công
    if response.status_code == 200:
        # Lưu ảnh vào file
        with open("Files/" + file_name, "wb") as f:
            f.write(response.content)
        return "✅ Đã tải file: " + file_name
    else:
        return "❌ Lỗi khi tải file. Vui lòng thử lại sau: " + response.text

# Xóa file đã tải về
def delete_local_file(file_name):
    try:
        subprocess.run(["del", "Files\\" + file_name], shell=True, check=True)
        return "✅ Đã xóa file: " + file_name
    except subprocess.CalledProcessError:
        return "⚠️ File không tồn tại hoặc không thể xóa: " + file_name
    
# Gửi file đến thiết bị
def push_file_to_device(device_id, file_name, remote_path="/sdcard/Download/"):
    try:
        download_file_from_server(file_name)
        subprocess.run(["platform-tools\\adb", "-s", device_id, "push", "Files/" + file_name, remote_path + file_name], check=True)
        subprocess.run([
            "platform-tools\\adb", "-s", device_id,
            "shell", "am", "broadcast",
            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file://{remote_path + file_name}"
        ], check=True)
    except subprocess.CalledProcessError:
        print("❌ Lỗi khi gửi file. Kiểm tra kết nối hoặc đường dẫn.")
    finally:
        delete_local_file(file_name)

# Xóa file trên thiết bị
def delete_file(device_id, file_name, remote_path="/sdcard/Download/"):
    try:
        subprocess.run(["platform-tools\\adb", "-s", device_id, "shell", f"rm '{remote_path + file_name}'"], check=True)
        print(f"✅ Đã xóa file: {remote_path + file_name}")
    except subprocess.CalledProcessError:
        print(f"⚠️ File không tồn tại hoặc không thể xóa: {remote_path + file_name}")

# Lấy nội dung clipboard
def get_clipboard_content(driver, app):
    driver.app_start("com.termux")
    driver.send_keys("termux-clipboard-get > /storage/emulated/0/Android/data/com.termux/files/clip.txt\n")
    time.sleep(2)
    driver.app_start(app)
    # Tên file lưu trên máy tính
    local_filename = "clipboard.txt"
    # Đường dẫn file trên thiết bị Android
    remote_path = "/storage/emulated/0/Android/data/com.termux/files/clip.txt"

    # Lệnh adb pull
    command = ["platform-tools/adb", "pull", remote_path, local_filename]
    subprocess.run(command, capture_output=True, text=True)

    # Mở file được pull về và đọc nội dung
    with open(local_filename, "r") as file:
        return file.read()

# Lấy liên kết bài viết
def extract_post_link(driver, post):
    for node in post.iter():
        if node.attrib.get("text") == "Chia sẻ" or node.attrib.get("content-desc") == "Chia sẻ":
            bounds = parse_number(node.attrib.get("bounds"))
            driver.click((bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2)
    time.sleep(1)
    click_template(driver, "copy_link")
    return get_clipboard_content(driver, "com.facebook.katana")

# Lấy liên kết trang cá nhân
def extract_facebook_user_link(driver):
    button = driver(description="Xem cài đặt khác của trang cá nhân")
    if button.exists(timeout=1):
        button.click()
    click_template(driver, "copy_profile_link")
    link = get_clipboard_content(driver, "com.facebook.katana")
    time.sleep(1)
    driver(resourceId="com.android.systemui:id/back").click()
    time.sleep(1)
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
def extract_comment_info(driver, comment_node, raw_comments):
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
        return None
    raw_comments.append(comment)

    # Lấy bounds và cắt ảnh
    bounds_str = driver.xpath(comment_node).get().attrib.get("bounds", "")
    bounds = parse_number(bounds_str)
    screen = driver.screenshot(format='opencv')
    screen = screen[bounds[1]:bounds[3], bounds[0]:bounds[2]]

    # Trích xuất thời gian từ ảnh
    time_texts = extract_time_from_image(screen)

    # Lấy tên và link người bình luận
    commenter_node.click()
    driver(text="Xem trang cá nhân").click()
    link = extract_facebook_user_link(driver)
    driver(resourceId="com.android.systemui:id/back").click()
    name = "<a href='" + link + "'>" + commenter_node.info.get("text", "").strip() + "</a>"

    # Lấy tên và link trong comment
    for child, text in link_nodes:
        child.click()
        link = extract_facebook_user_link(driver)
        comment = comment.replace(text, "<a href='" + link + "'>" + text + "</a>")
        
    return {
        "name": name,
        "comment": comment,
        "time": time_texts
    }