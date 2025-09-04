import uiautomator2 as u2
from module import *
driver = u2.connect("F6NZ5LRKWWGACYQ8")
driver.app_start("com.facebook.katana")


asyncio.run(add_friend(driver, '22615833'))