from fb_task import *
from sending_message_and_adding_friend import DeviceHandler
import uiautomator2 as u2
import asyncio
import logging
import time
import json
from typing import Optional, Callable
import sys
sys.stdout.reconfigure(encoding='utf-8')

from module import *
from util import *
import main_lib
import pymongo_management

# ======================= CẤU HÌNH =======================
HOME_PACKAGES = {
    "com.android.launcher",
    "com.google.android.apps.nexuslauncher",
    "com.sec.android.app.launcher",
    "com.miui.home",
    "com.oppo.launcher",
    "com.bbk.launcher2",
    "com.vivo.launcher",
    "com.huawei.android.launcher",
    "com.teslacoilsw.launcher",
}
ZALO_PKG = "com.zing.zalo"
FACEBOOK_PKG = "com.facebook.katana"
TARGET_PACKAGES = {ZALO_PKG, FACEBOOK_PKG}

# Một lần bật 1.1.1.1 cho mỗi device (per-process memory)
_VPN_CHECKED = set()
_STATUS_FILE_CHECK = set()

# ======================= HÀM HỖ TRỢ =======================
def _is_home_pkg(pkg: str) -> bool:
    return pkg in HOME_PACKAGES

def _is_target_pkg(pkg: str) -> bool:
    return pkg in TARGET_PACKAGES

async def ensure_1111_vpn_on_once(driver, device_id: str):
    """
    Bật app 1.1.1.1 và gạt switch nếu chưa bật — chỉ 1 lần cho mỗi device_id.
    Khoan fail nếu không có app.
    """
    if device_id in _VPN_CHECKED:
        return
    _VPN_CHECKED.add(device_id)
    try:
        log_message(f"[{device_id}] Kiểm tra bật 1.1.1.1 (một lần)")
        # Mở app 1.1.1.1
        driver.app_start("com.cloudflare.onedotonedotonedotone")
        await asyncio.sleep(3.0)

        # Tìm switch và bật nếu đang tắt
        sw = driver(resourceId="com.cloudflare.onedotonedotonedotone:id/launchSwitch")
        if sw.exists:
            try:
                checked = bool(sw.info.get("checked"))
            except Exception:
                checked = False
            if not checked:
                sw.click()
                await asyncio.sleep(1.5)

        # Không tắt app để giữ VPN chạy nền
        log_message(f"[{device_id}] One-time check 1.1.1.1 OK")
    except Exception as e:
        log_message(f"[{device_id}] VPN one-time check lỗi: {e}", logging.WARNING)

async def disable_auto_rotation(driver, device_id: str):
    """
    Thực sự tắt chế độ tự động xoay màn hình của hệ thống Android
    """
    
    def parse_shell_response(result):
        """Helper function để xử lý ShellResponse object từ UIAutomator2"""
        if hasattr(result, 'output'):
            return result.output.strip()
        elif hasattr(result, 'text'):
            return result.text.strip()
        elif hasattr(result, 'stdout'):
            return result.stdout.strip()
        else:
            return str(result).strip()
    
    try:
        log_message(f"[{device_id}] Tắt chế độ tự động xoay màn hình hệ thống")
        
        # Kiểm tra trạng thái hiện tại trước
        try:
            current_result = driver.shell("settings get system accelerometer_rotation")
            current_value = parse_shell_response(current_result)
            log_message(f"[{device_id}] Trạng thái auto-rotation hiện tại: {current_value}")
        except Exception as e:
            log_message(f"[{device_id}] Không thể kiểm tra trạng thái hiện tại: {e}")
            current_value = "unknown"
        
        # Tắt auto-rotation qua shell command
        try:
            driver.shell("settings put system accelerometer_rotation 0")
            log_message(f"[{device_id}] Đã gửi lệnh tắt auto-rotation qua settings")
            await asyncio.sleep(1)  # Chờ settings apply
            
        except Exception as e:
            log_message(f"[{device_id}] Lỗi tắt auto-rotation qua settings: {e}")
        
        # Kiểm tra trạng thái sau khi tắt
        try:
            result = driver.shell("settings get system accelerometer_rotation")
            final_value = parse_shell_response(result)
            
            if final_value == "0":
                status = "TẮT ✅"
                log_message(f"[{device_id}] Auto-rotation đã được TẮT thành công!")
            elif final_value == "1":
                status = "BẬT ❌"
                log_message(f"[{device_id}] Auto-rotation vẫn còn BẬT - có thể cần retry", logging.WARNING)
            else:
                status = f"KHÔNG XÁC ĐỊNH ({final_value})"
                log_message(f"[{device_id}] Trạng thái auto-rotation không xác định: {final_value}", logging.WARNING)
            
            log_message(f"[{device_id}] Trạng thái auto-rotation cuối: {status}")
            
        except Exception as e:
            log_message(f"[{device_id}] Không thể kiểm tra trạng thái cuối: {e}")
        
        log_message(f"[{device_id}] Hoàn thành disable auto-rotation")
        
    except Exception as e:
        log_message(f"[{device_id}] Lỗi khi tắt auto-rotation: {e}", logging.WARNING)

class InactivityWatchdog:
    def __init__(
        self,
        driver,
        device_id: str,
        idle_seconds: int = 60,
        on_resume: Optional[Callable[[str], "asyncio.Future"]] = None,
        on_restart: Optional[Callable[[], "asyncio.Future"]] = None,
        phase_provider: Optional[Callable[[], str]] = None,
    ):
        self.driver = driver
        self.device_id = device_id
        self.idle_seconds = int(idle_seconds)
        self.on_resume = on_resume
        self.on_restart = on_restart
        self.phase_provider = phase_provider or (lambda: "facebook")
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()

        self._last_seen_target = time.time()
        self._home_since: Optional[float] = None

    def log(self, msg: str, level=logging.INFO):
        try:
            log_message(f"[{self.device_id}][Watchdog] {msg}", level)
        except Exception:
            print(f"[{self.device_id}][Watchdog] {msg}")

    async def start(self):
        if self._task is None:
            self._stop.clear()
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        if self._task:
            self._stop.set()
            try:
                await self._task
            except Exception:
                pass
            self._task = None

    async def _run(self):
        while not self._stop.is_set():
            # Đọc app hiện tại
            try:
                info = await asyncio.to_thread(self.driver.app_current)
                pkg = (info or {}).get("package", "") or ""
            except Exception:
                pkg = ""

            now = time.time()

            # Cập nhật lần cuối thấy target
            if _is_target_pkg(pkg):
                self._last_seen_target = now
                self._home_since = None  # reset
            elif _is_home_pkg(pkg):
                if self._home_since is None:
                    self._home_since = now
            else:
                # ở app khác, không reset _home_since
                pass

            # Nếu ở HOME quá 12s -> resume app theo phase
            if self._home_since and now - self._home_since >= 12:
                self._home_since = None  # tránh spam
                if self.on_resume:
                    phase = self.phase_provider()
                    self.log(f"HOME >12s → mở lại app theo phase='{phase}'")
                    try:
                        await self.on_resume(phase)
                    except Exception as e:
                        self.log(f"Lỗi on_resume: {e}", logging.WARNING)

            # Nếu KHÔNG thấy Zalo/Facebook >= idle_seconds -> yêu cầu restart
            if now - self._last_seen_target >= self.idle_seconds:
                self.log(f"Không thấy Zalo/Facebook ≥ {self.idle_seconds}s → yêu cầu RESTART", logging.WARNING)
                if self.on_restart:
                    try:
                        await self.on_restart()
                    except Exception as e:
                        self.log(f"Lỗi on_restart: {e}", logging.ERROR)
                # Sau khi báo restart thì dừng watchdog
                break

            await asyncio.sleep(3.0)


# ======================= LUỒNG THIẾT BỊ =======================
class RestartThisDevice(Exception):
    pass

async def device_once(device_id: str):
    """
    Chạy một vòng đầy đủ cho MỘT thiết bị:
      - Kết nối
      - Tắt auto-rotation để tránh xoay màn hình
      - Bật VPN 1.1.1.1 nếu cần (1 lần)
      - Watchdog chạy nền
      - Pha 'zalo' (một vòng) -> Pha 'facebook'
    """
    # Kết nối thiết bị
    driver = await asyncio.to_thread(u2.connect_usb, device_id)
    handler = DeviceHandler(driver, device_id)
    await handler.connect()
    
    # Tắt chế độ tự động xoay màn hình
    await disable_auto_rotation(driver, device_id)

    # Bật 1.1.1.1 (một lần)
    await ensure_1111_vpn_on_once(driver, device_id)

    # Kiểm tra cài đặt Termux và termux-api
    result = await main_lib.check_termux_api_installed(driver)
    if not result:
        await asyncio.sleep(60)
        return
    
    # Trạng thái pha hiện tại để watchdog biết cần resume app nào khi về HOME
    current_phase = {"value": "zalo"}

    # Cờ yêu cầu restart từ watchdog
    restart_event = asyncio.Event()

    async def _on_resume(phase: str):
        # Mở lại đúng app theo phase
        if phase == "zalo":
            driver.app_start(ZALO_PKG)
        else:
            driver.app_start(FACEBOOK_PKG)
        await asyncio.sleep(2.0)

    async def _on_restart():
        # Dọn app để về trạng thái sạch rồi bật cờ restart
        try:
            driver.app_stop(ZALO_PKG)
        except Exception:
            pass
        try:
            driver.app_stop(FACEBOOK_PKG)
        except Exception:
            pass
        restart_event.set()

    # Watchdog
    watchdog = InactivityWatchdog(
        driver=driver,
        device_id=device_id,
        idle_seconds=60,
        on_resume=_on_resume,
        on_restart=_on_restart,
        phase_provider=lambda: current_phase["value"],
    )
    await watchdog.start()
    await pymongo_management.update_device_status(device_id, True)  # Cập nhật thiết bị thành online
    try:

        # ===== PHA FACEBOOK =====
        current_phase["value"] = "facebook"
        # Chạy flow Facebook như thường lệ
        await run_on_device_original(driver)

        if restart_event.is_set():
            raise RestartThisDevice("RESTART_THIS_DEVICE (sau pha Facebook)")
        
        # ===== PHA ZALO =====
        current_phase["value"] = "zalo"
        # Đảm bảo đang mở Zalo trước khi chạy
        driver.app_start(ZALO_PKG)
        await asyncio.sleep(2.0)
        await asyncio.to_thread(handler.run, 1)

        if restart_event.is_set():
            raise RestartThisDevice("RESTART_THIS_DEVICE (sau pha Zalo)")

    finally:
        await watchdog.stop()

async def check_driver(driver):
    try:
        _ = driver.info
        return True
    except Exception:
        return False
    
async def device_supervisor(device_id: str):
    """
    Giám sát riêng từng thiết bị:
      - Nếu watchdog yêu cầu restart -> chạy lại from-scratch chỉ cho thiết bị đó.
      - Không ảnh hưởng các thiết bị khác.
    """
    while True:
        try:
            driver = await asyncio.to_thread(u2.connect_usb, device_id)
            break
        except:
            pass
    task = None
    temp_alive = True
    device_status_path = f"C:/Zalo_CRM/Zalo_base/device_status_{device_id}.json"
    await main_lib.reset_active()  # Đặt lại tất cả device về inactive khi khởi động
    while True:
        try:
            # ======================= NEW CODE BLOCK START =======================
            # Vòng lặp chờ, liên tục kiểm tra file status trước khi làm bất cứ điều gì
            while True:
                still_alive = await check_driver(driver)
                if not temp_alive and still_alive:
                    log_message(f"[{device_id}] ✅ Kết nối thiết bị đã được khôi phục.", logging.INFO)
                    await pymongo_management.update_device_status(device_id, True)
                temp_alive = still_alive
                if not still_alive:
                    if task is not None and not task.done():
                        task.cancel()
                        log_message(f"[{device_id}] ❌ Mất kết nối thiết bị, hủy task đang chạy.", logging.WARNING)
                        await pymongo_management.update_device_status(device_id, False)
                    await asyncio.sleep(5.0)
                    driver = await asyncio.to_thread(u2.connect_usb, device_id)
                    continue
                is_paused = False  
                try:
                    with open(device_status_path, 'r', encoding='utf-8') as f:
                        device_status = json.load(f)
                    # Nếu 'active' là True, thiết bị sẽ bị tạm dừng
                    if device_status.get('active', False):
                        is_paused = True
                    _STATUS_FILE_CHECK.discard(device_id)  # Đã tìm thấy file, xóa khỏi set
                except FileNotFoundError:
                    # File không tồn tại, coi như không tạm dừng, cho phép chạy
                    if not device_id in _STATUS_FILE_CHECK:
                        log_message(f"[{device_id}] ✅ Không tìm thấy file status, tiếp tục chạy.", logging.WARNING)
                        _STATUS_FILE_CHECK.add(device_id)
                    pass
                except Exception as e:
                    log_message(f"[{device_id}] ❌ Lỗi: {e}, tiếp tục chạy.", logging.WARNING)
                if is_paused and task is not None:
                    if not task.done():
                        task.cancel()
                        log_message(f"[{device_id}] ⏸️ Phát hiện tạm dừng từ file status, hủy task đang chạy.", logging.WARNING)
                    await asyncio.sleep(2)
                    continue
                else:
                    break
            # ======================= NEW CODE BLOCK END =======================
            
            if task is None or task.done():
                task = asyncio.create_task(device_once(device_id))
            await asyncio.sleep(2.0)
        except RestartThisDevice as e:
            log_message(f"[{device_id}] ↻ Watchdog yêu cầu RESTART — khởi động lại quy trình cho máy này.", logging.WARNING)
            await asyncio.sleep(2.0)
            continue
        except Exception as e:
            if await check_driver(driver):
                log_message(f"[{device_id}] Lỗi không mong muốn: {e}. Sẽ thử chạy lại sau.", logging.ERROR)
            await asyncio.sleep(5.0)
            continue

async def run_all_devices():
    """Chạy tất cả device với Task Manager và WebSocket"""
    # Khởi động supervisor cho mỗi device
    tasks = [asyncio.create_task(device_supervisor(did)) for did in DEVICE_LIST]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(run_all_devices())
    except KeyboardInterrupt:
        print("[!] Dừng bằng bàn phím (KeyboardInterrupt)")
        asyncio.run(pymongo_management.update_device_status(None, False))  # Cập nhật tất cả thiết bị thành offline
    except Exception as e:
        log_message(f"Lỗi chạy chính: {e}", logging.ERROR)
        asyncio.run(pymongo_management.update_device_status(None, False))  # Cập nhật tất cả thiết bị thành offline