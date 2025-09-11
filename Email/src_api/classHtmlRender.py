import uiautomator2 as u2
import time
import os
import json
from filelock import FileLock


class HtmlRenderSimulator:
    def __init__(self, EMP_ID: int, BUSINESS_SUBJECT_PATH: str, BUSINESS_WRITEN_MAIL_PATH: str,  MODE:int=2):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.EMP_ID = str(EMP_ID)
        
        self.JSON_FILE = os.path.join(self.BASE_DIR, "..", "business", "business_info.json")
        LOCK_FILE = self.JSON_FILE + ".lock"
        with FileLock(LOCK_FILE, timeout=10):
            with open(self.JSON_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            
        self.device_id = self.data[self.EMP_ID]["device"]
        self.d = u2.connect(self.device_id)
        self.width, self.height = self.d.window_size()
        
        self.MODE = 2  # 1: mặc định 2: kinh doanh nhập 
        if self.MODE == 1:
            self.BUSINESS_SUBJECT_PATH = os.path.join(self.BASE_DIR, "..", "business", "business_subject_sample.txt")
            self.BUSINESS_WRITEN_MAIL_PATH = os.path.join(self.BASE_DIR, "..", "business", "business_writen_mail_sample.txt")
        else: 
            self.BUSINESS_SUBJECT_PATH = BUSINESS_SUBJECT_PATH
            self.BUSINESS_WRITEN_MAIL_PATH = BUSINESS_WRITEN_MAIL_PATH

        
        
        self.BUSINESS_SUBJECT = self.get_subject()
        self.BUSINESS_WRITEN_MAIL = self.get_content()

    def get_subject(self):
        """Lấy subject"""
        with open (self.BUSINESS_SUBJECT_PATH, "r", encoding="utf-8") as f:
            BUSINESS_SUBJECT = f.read().strip()
        return BUSINESS_SUBJECT

    def get_content(self):
        """Lấy content"""
        with open (self.BUSINESS_WRITEN_MAIL_PATH, "r", encoding="utf-8") as f:
            BUSINESS_WRITEN_MAIL = f.read().strip()
        return BUSINESS_WRITEN_MAIL
    
    def set_subject(self, text:str):
        "Nhận kết quả từ đầu vào api để viết lại file txt"
        if self.MODE == 2:
            lock = FileLock(self.BUSINESS_SUBJECT_PATH + ".lock")
            with lock:
                with open(self.BUSINESS_SUBJECT_PATH, "w", encoding="utf-8") as f:
                    f.write(text)
            self.BUSINESS_SUBJECT = text
        
    def set_content(self, text:str):
        """
        Nhận kết quả từ đầu vào api để viết lại file txt, text ở đây đang là html raw
        """
        if self.MODE == 2:
            lock = FileLock(self.BUSINESS_WRITEN_MAIL_PATH + ".lock")
            with lock:
                with open(self.BUSINESS_WRITEN_MAIL_PATH, "w", encoding="utf-8") as f:
                    f.write(text)
            self.BUSINESS_WRITEN_MAIL = text
    
    def beautify_html(self):
        """Chuyển text dạng html thành text render có format"""
        self.open_html_app()
        self.search_html_online_viewer()
        self.compile_html()

        return None
    
    def open_html_app(self):
        """
        Mở app HTML Editor trên thiết bị
        Lưu ý khi mở app phải ở trong thẻ .html rồi 
        sử dụng weditor để dễ bề biết trước xpath
        """
        self.d(resourceId="com.android.systemui:id/center_group").click()
        time.sleep(1)
        self.d.swipe_ext("up", scale=0.8)
        time.sleep(1)
        self.d(resourceId="com.gogo.launcher:id/search_container_all_apps").click()
        time.sleep(1)
        # tìm google, bắt buộc phải đăng nhập và hiện giao diện google rồi
        self.d.send_keys("Google", clear=True)
        time.sleep(1)
        self.d(resourceId="com.gogo.launcher:id/icon", text="Google").click()
        time.sleep(1)
        print("Đang mở Google...")
        
        self.search_html_online_viewer()
        
    def search_html_online_viewer(self):
        """Mở đúng website htmlonlineviewer"""
        if self.d(resourceId="com.android.chrome:id/url_bar", textContains="html.onlineviewer.net").exists(timeout=2):
            print("Đúng trang HTML Online Viewer rồi → clear luôn")
            self.clear_old_html()
        else:
            self.delete_recent_tab()
            # nhấp tìm kiếm
            self.d.xpath('//*[@resource-id="googleapp_facade_search_box"]/android.widget.TextView[1]').click()
            self.d(resourceId="com.google.android.googlequicksearchbox:id/googleapp_search_box").click()
            # truyền tên miền 
            self.d.send_keys("https://html.onlineviewer.net/", clear=True)
            self.d.xpath('//*[@resource-id="com.google.android.inputmethod.latin:id/key_pos_ime_action"]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').click()
            time.sleep(3)
            self.clear_old_html()
        
    def clear_old_html(self):
        # 476, 0.21
        x = self.width * 0.476
        y = self.height * 0.210
        self.d.long_click(x, y, duration=1.0)
        time.sleep(1)
        self.d(resourceId="android:id/overflow").click()
        time.sleep(1)
        
        if self.d(text="Chọn tất cả").exists(timeout=3):
            self.d(text="Chọn tất cả").click()
            time.sleep(1.5)
        else:
            print("Không tìm thấy tuỳ chọn Chọn tất cả")
        # chọn tất rồi lại nhấn giữ để cắt
        self.d.long_click(x, y, duration=1.0)
        time.sleep(1)
        if self.d(text="Cắt").exists(timeout=3):
            self.d(text="Cắt").click()
            time.sleep(1.5)
            print("Đã xoá cũ")
        else:
            print("Không tìm thấy tuỳ chọn Cắt")
            self.d.send_keys(self.BUSINESS_WRITEN_MAIL, clear=True)
        self.d.send_keys(self.BUSINESS_WRITEN_MAIL)
        
    def compile_html(self):
        # 0.794, 0.305
        x = self.width * 0.794
        y = self.height * 0.305
        self.d.long_click(x, y, duration=1.0)
        time.sleep(1)
        self.d(resourceId="android:id/overflow").click()
        time.sleep(1)
        # chọn tất rồi sao chép
        if self.d(text="Chọn tất cả").exists(timeout=3):
            self.d(text="Chọn tất cả").click()
            time.sleep(1.5)
            self.d(text="SAo chép").click()
            time.sleep(1)
        else:
            print("Không tìm thấy tuỳ chọn Chọn tất cả")
            # ảnh Cả cook tiếp nhé, đoạn này nếu cơ chế giữ để hiện menu nếu thay đổi thì toang, phải chinh lại mấy hàm này
        
    def delete_recent_tab(self):
        self.d(resourceId="com.android.systemui:id/recent_apps").click()
        	# (0.476, 0.48)
        self.d.swipe_ext("up", scale=0.8, box=(0.3, 0.3, 0.7, 0.6))
            
            
def run_simulator(EMP_ID, BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH, MODE):
    simulator = HtmlRenderSimulator(EMP_ID=EMP_ID, BUSINESS_SUBJECT_PATH=BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH=BUSINESS_WRITEN_MAIL_PATH, MODE=MODE)
    return simulator
