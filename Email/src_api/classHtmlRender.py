import uiautomator2 as u2
import time
import os
import json
from filelock import FileLock


class HtmlRenderSimulator:
    def __init__(self, EMP_ID: int, customer_id: int = None, MODE=2):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.EMP_ID = str(EMP_ID)
        self.customer_id = customer_id
        self.MODE = MODE
        self.html_processed = False
        # Database path
        self.DB_PATH = os.path.join(self.BASE_DIR, "..", "business", "business.db")
        
        # Get device info from employees table
        self.device_id = self.get_device_id()
        self.d = u2.connect(self.device_id)
        self.width, self.height = self.d.window_size()
        
        # Get email content from database
        self.BUSINESS_SUBJECT = None
        self.BUSINESS_WRITEN_MAIL = None
        
        if self.customer_id:
            self.load_customer_data()

    def get_device_id(self):
        """Lấy device_id từ bảng employees"""
        conn = None
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT device FROM employees WHERE emp_id = ?", (self.EMP_ID,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                raise ValueError(f"Employee ID {self.EMP_ID} not found in database")
                
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    def load_customer_data(self):
        """Load subject và content từ bảng customers"""
        conn = None
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT subject, content FROM customers WHERE customer_id = ? AND emp_id = ?", 
                (self.customer_id, self.EMP_ID)
            )
            result = cursor.fetchone()
            
            if result:
                self.BUSINESS_SUBJECT = result[0] if result[0] else ""
                self.BUSINESS_WRITEN_MAIL = result[1] if result[1] else ""
            else:
                raise ValueError(f"Customer ID {self.customer_id} not found for employee {self.EMP_ID}")
                
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    def get_subject(self):
        """Lấy subject từ database"""
        if self.BUSINESS_SUBJECT is None and self.customer_id:
            self.load_customer_data()
        return self.BUSINESS_SUBJECT if self.BUSINESS_SUBJECT else ""

    def get_content(self):
        """Lấy content từ database"""
        if self.BUSINESS_WRITEN_MAIL is None and self.customer_id:
            self.load_customer_data()
        return self.BUSINESS_WRITEN_MAIL if self.BUSINESS_WRITEN_MAIL else ""
    
    
    def beautify_html(self):
        """Chuyển text dạng html thành text render có format"""
        if self.html_processed:
            print("HTML đã được xử lý rồi")
            return None
        # chạy lấy rendered text
        self.open_html_app()
        self.search_html_online_viewer()
        self.compile_html()
        
        print("HTML processing hoàn thành, chờ 5s...")
        time.sleep(5)
        self.html_processed = True
        print("HTML processing đã được đánh dấu hoàn thành")

        return None
    
    def open_html_app(self):
        """
        Mở app Google trên thiết bị
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
            # nhấp tìm kiếm
            self.d.xpath('//*[@resource-id="googleapp_facade_search_box"]/android.widget.TextView[1]').click()
            time.sleep(1)
            self.d(resourceId="com.google.android.googlequicksearchbox:id/googleapp_search_box").click()
            # truyền tên miền 
            self.d.send_keys("https://html.onlineviewer.net/", clear=True)
            time.sleep(1)
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
        time.sleep(1)
        self.d.swipe(0.476, 0.74, 0.476, 0.0)
        time.sleep(1)
        self.d(resourceId="com.android.systemui:id/center_group").click()
        time.sleep(1)
        
def run_simulator(EMP_ID, BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH, MODE):
    simulator = HtmlRenderSimulator(EMP_ID=EMP_ID, BUSINESS_SUBJECT_PATH=BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH=BUSINESS_WRITEN_MAIL_PATH, MODE=MODE)
    return simulator
