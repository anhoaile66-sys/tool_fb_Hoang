import uiautomator2 as u2
import time
import os
import json
from filelock import FileLock


class HtmlRenderSimulator:
    def __init__(self, EMP_ID: int, BUSINESS_SUBJECT_PATH: str, BUSINESS_WRITEN_MAIL_PATH: str,  MODE:int=2):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.EMP_ID = str(EMP_ID)
        
        self.JSON_FILE = os.path.join(self.BASE_DIR, "business_info.json")
        LOCK_FILE = self.JSON_FILE + ".lock"
        with FileLock(LOCK_FILE, timeout=10):
            with open(self.JSON_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            
        self.device_id = self.data[self.EMP_ID]["device"]
        self.d = u2.connect(self.device_id)
        self.width, self.height = self.d.window_size()
        
        self.MODE = MODE  # 1: mặc định 2: kinh doanh nhập 
        if self.MODE == 1:
            self.BUSINESS_SUBJECT_PATH = os.path.join(self.BASE_DIR, "business_subject_sample.txt")
            self.BUSINESS_WRITEN_MAIL_PATH = os.path.join(self.BASE_DIR, "business_writen_mail_sample.txt")
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
        self.clear_old_html()
        self.compile_html()
        self.go_back_code_html()
        return None
    
    def open_html_app(self):
        """
        Mở app HTML Editor trên thiết bị
        Lưu ý khi mở app phải ở trong thẻ .html rồi 
        sử dụng weditor để dễ bề biết trước xpath
        """
        self.d(resourceId="com.android.systemui:id/center_group").click()
        self.d.swipe_ext("up", scale=0.8)
        time.sleep(1)
        self.d(resourceId="com.gogo.launcher:id/search_container_all_apps").click()
        time.sleep(1)
        self.d.send_keys("Html Editor", clear=True)
        time.sleep(1)
        self.d(resourceId="com.gogo.launcher:id/icon").click()
        time.sleep(1)
        print("Đang mở app HTML Editor...")
        
    def clear_old_html(self):
        x = self.width * 0.325
        y = self.height * 0.323
        self.d.long_click(x, y, duration=1.0)
        time.sleep(1)
        if self.d(text="Select all").exists(timeout=3):
            self.d(text="Select all").click()
            time.sleep(1.5)
            self.d.press("del")
            print("Đã xoá cũ")
        else:
            print("Không tìm thấy tuỳ chọn Select all")

        self.d.send_keys(self.BUSINESS_WRITEN_MAIL)
        
    def compile_html(self):
        self.d(description="Run").click()
        time.sleep(2)
        x = self.width * 0.058
        y = self.height * 0.193
        self.d.long_click(x, y, duration=1.0)
        time.sleep(1)
        if self.d(text="Chọn tất cả").exists(timeout=3):
            self.d(text="Chọn tất cả").click()
            time.sleep(0.5)
            self.d(text="Sao chép").click()
        elif self.d(text="Select all").exists(timeout=3):
            self.d(text="Select all").click()
            time.sleep(0.5)
            self.d(text="Copy").click()
        else:
            print("Không tìm thấy tuỳ chọn Select all")
            # anh Cả quất tiếp nhé
        
    def go_back_code_html(self):
        self.d.xpath('//android.widget.ScrollView/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.widget.TextView[1]').click()
            
            
def run_simulator(EMP_ID, BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH, MODE):
    simulator = HtmlRenderSimulator(EMP_ID=EMP_ID, BUSINESS_SUBJECT_PATH=BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH=BUSINESS_WRITEN_MAIL_PATH, MODE=MODE)
    return simulator
    