from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options  # Thêm dòng này
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = UiAutomator2Options().load_capabilities({
    "platformName": "Android",
    "udid": "c7326412",
    "appPackage": "com.opera.browser",
    "appActivity": "com.opera.Opera",
    "noReset": True,
    "autoLaunch": False,
    "automationName": "UiAutomator2"
})

driver = webdriver.Remote("http://localhost:4723", options = options)

wait = WebDriverWait(driver,100)

def box_check():
    tick_box = driver.find_elements(
        AppiumBy.
    )