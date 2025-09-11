import uiautomator2 as u2
import time
d = u2.connect('8HMN4T9575HAQWLN')
d(resourceId="com.android.systemui:id/recent_apps").click()
time.sleep(1)
d.swipe(0.476, 0.74, 0.476, 0.0)
time.sleep(1)
d(resourceId="com.android.systemui:id/center_group").click()
time.sleep(1)