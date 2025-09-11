import uiautomator2 as u2
import time
d = u2.connect('8HMN4T9575HAQWLN')
d(resourceId="com.android.systemui:id/recent_apps").click()
time.sleep(1)
d.swipe(0.476, 0.74, 0.476, 0.0)
time.sleep(1)
d(resourceId="com.android.systemui:id/center_group").click()
time.sleep(1)

    # def add_file(self, name_file):
    #     self.d(resourceId="com.google.android.gm:id/add_attachment").click()
    #     time.sleep(1)
    #     self.d.xpath('//android.widget.ListView/android.widget.LinearLayout[3]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]').click()
    #     time.sleep(3)
    #     self.d(description="Hiển thị gốc").click()
    #     time.sleep(1)
    #     self.d(resourceId="android:id/title", text="Tài liệu").click()
    #     time.sleep(1)
    #     self.d(resourceId="com.google.android.documentsui:id/option_menu_search").click()
    #     time.sleep(1)
    #     self.d(resourceId="com.google.android.documentsui:id/search_src_text").click()
    #     time.sleep(1)
    #     self.d.send_keys(name_file, clear=True)
    #     time.sleep(1)
    #     self.d(resourceId="com.google.android.documentsui:id/thumbnail").click()
    #     # chọn được là sẽ quay lại mail
    #     time.sleep(2)