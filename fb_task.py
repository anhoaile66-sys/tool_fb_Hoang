import asyncio
import time
from util import *
from module import *
from datetime import datetime, timedelta

# Thoát app, xóa cache khi chờ task
async def clear_app(driver):
    driver.press("recent")
    await asyncio.sleep(2)

    size = driver.window_size()
    width, height = size[0], size[1]

    start_x = width / 2
    end_x = start_x
    start_y = height * 0.7
    end_y = height * 0.2
    duration = 0.04

    driver.swipe(start_x, start_y, end_x, end_y, duration=duration)
    await asyncio.sleep(3)
    driver.press("home")
    driver.press("back")

async def fb_natural_task(driver, emp_id:str, account: str):
    actions = [
        ("Xem story", lambda: watch_story(driver)),
        ("Lướt fb", lambda: surf_fb(driver)),
        # ("Kết bạn", lambda: add_friend(driver, emp_id)),
        # ("Kiểm tra bài đăng", lambda: check_post(driver, account)),
        # ("Kiểm tra nhóm chờ duyệt", lambda: check_unapproved_groups(driver, account)),
        ("Bình luận thương hiệu", lambda: comment_recruitment_post(driver, account)),
        # ("Nhận lệnh từ CRM", lambda: get_commands(driver, account))
    ]

    # Random hóa thứ tự các hành động
    random.shuffle(actions)
    log_message(f"\n\nThực hiện tác vụ: Xem reels\n")

    await watch_reels(driver)
    await asyncio.sleep(random.uniform(4,6))

    for name, action in actions:
        log_message(f"\n\n{driver.serial} Thực hiện tác vụ: {name}\n", logging.INFO)

        await action()
        await asyncio.sleep(random.uniform(4,6))

    log_message("Hoàn thành 1 chuỗi task")

async def run_on_device(driver, stop_event=None, pause_event=None, resume_event=None):
    """
    Chạy task Facebook với khả năng interrupt
    """
    try:
        device_id = driver.serial

        # Check interrupt trước khi bắt đầu
        if stop_event and stop_event.is_set():
            log_message(f"[{device_id}] Facebook task stopped before start", logging.INFO)
            return

        # await clear_app(driver)
        driver.press("home")
        driver.app_start("com.facebook.katana", ".LoginActivity")
        
        # Wait với khả năng interrupt
        await interruptible_sleep(random.uniform(10,15), stop_event, pause_event, resume_event)

        device = load_device_account(device_id)
        if not device:
            log_message(f"Không tìm thấy dữ liệu cho thiết bị {device_id}", logging.WARNING)
            emp_id = "22615833"
            account = "default"
        else:
            emp_id = device['user']['emp_id']
            account = device['current_account']
            
            # Check interrupt trước khi chuyển tài khoản
            if stop_event and stop_event.is_set():
                log_message(f"[{device_id}] Facebook task stopped during account check", logging.INFO)
                return
                
            # Chuyển tài khoản
            last_time = device['time_logged_in']
            if last_time and (datetime.fromisoformat(last_time) + timedelta(hours=random.randint(4,6))) < datetime.now():
                # Đủ thời gian, chuyển tài khoản
                i=0
                for acc in device['accounts']:
                    i+=1
                    if acc['account'] == device['current_account']:
                        break
                if i==3: i=0
                for acc in device['accounts']:
                    if i==0:
                        account=acc
                        break
                    i-=1
                log_message(f"Đang đăng nhập vào tài khoản {account['name']} trên thiết bị {device_id}")
                await swap_account_interruptible(driver, account, stop_event, pause_event, resume_event)
                device['current_account'] = account['account']
                update_current_account(device_id, account)
        
        # Check interrupt trước khi chạy task chính
        if stop_event and stop_event.is_set():
            log_message(f"[{device_id}] Facebook task stopped before main tasks", logging.INFO)
            return
            
        # tasks nuôi fb với interrupt support
        await fb_natural_task_interruptible(driver, emp_id, account, stop_event, pause_event, resume_event)
        # await share_post(driver, text=random.choice(SHARES))
        
    except Exception as e:
        if stop_event and stop_event.is_set():
            log_message(f"[{device_id}] Facebook task interrupted: {e}", logging.INFO)
        else:
            log_message(f"Lỗi trên thiết bị {device_id}: {e}", logging.ERROR)

async def interruptible_sleep(duration, stop_event=None, pause_event=None, resume_event=None):
    """Sleep có thể bị interrupt và pause"""
    if not stop_event and not pause_event:
        await asyncio.sleep(duration)
        return
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Check stop
        if stop_event and stop_event.is_set():
            return
        
        # Check pause
        if pause_event and pause_event.is_set():
            log_message("Task paused, waiting for resume...", logging.INFO)
            if resume_event:
                await resume_event.wait()
            continue
        
        # Sleep trong interval ngắn để responsive
        sleep_time = min(1.0, end_time - time.time())
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

async def swap_account_interruptible(driver, account, stop_event=None, pause_event=None, resume_event=None):
    """Swap account với interrupt support"""
    try:
        # Check interrupt trước khi bắt đầu
        if stop_event and stop_event.is_set():
            log_message("swap_account interrupted before start", logging.INFO)
            return
            
        if pause_event and pause_event.is_set():
            log_message("swap_account paused", logging.INFO)
            if resume_event:
                await resume_event.wait()
            log_message("swap_account resumed", logging.INFO)
        
        # Gọi hàm swap_account gốc
        # Vì swap_account có thể không hỗ trợ interrupt, ta wrap nó
        await swap_account(driver, account)
        
        # Check interrupt sau khi hoàn thành
        if stop_event and stop_event.is_set():
            log_message("swap_account interrupted after completion", logging.INFO)
            return
            
    except Exception as e:
        if stop_event and stop_event.is_set():
            log_message(f"swap_account interrupted: {e}", logging.INFO)
        else:
            log_message(f"Error in swap_account_interruptible: {e}", logging.ERROR)
            raise e

async def run_task_with_interrupt(task_func, driver, stop_event=None, pause_event=None, resume_event=None):
    """Helper function để chạy task với interrupt support"""
    task = asyncio.create_task(task_func(driver))
    
    while not task.done():
        if stop_event and stop_event.is_set():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                log_message(f"{task_func.__name__} cancelled", logging.INFO)
            return
            
        if pause_event and pause_event.is_set():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            if resume_event:
                await resume_event.wait()
            task = asyncio.create_task(task_func(driver))
            continue
            
        await asyncio.sleep(0.5)
        
    if not task.cancelled():
        await task

async def fb_natural_task_interruptible(driver, emp_id, account, stop_event=None, pause_event=None, resume_event=None):
    """Facebook natural task với interrupt support"""
    try:
        # Định nghĩa actions như async functions thay vì lambda
        async def watch_story_action():
            await run_task_with_interrupt(watch_story, driver, stop_event, pause_event, resume_event)
            
        async def surf_fb_action():
            await run_task_with_interrupt(surf_fb, driver, stop_event, pause_event, resume_event)
            
        # async def add_friend_action():
        #     await add_friend(driver, emp_id)
            
        # async def check_post_action():
        #     await check_post(driver, account)
            
        # async def check_unapproved_groups_action():
        #     await check_unapproved_groups(driver, account)
            
        # async def comment_recruitment_post_action():
        #     await comment_recruitment_post(driver, account)
            
        # async def get_commands_action():
        #     await get_commands(driver, account)

        actions = [
            ("Xem story", watch_story_action),
            ("Lướt fb", surf_fb_action),
            # ("Kết bạn", add_friend_action),
            # ("Kiểm tra bài đăng", check_post_action),
            # ("Kiểm tra nhóm chờ duyệt", check_unapproved_groups_action),
            # ("Bình luận thương hiệu", comment_recruitment_post_action),
            # ("Nhận lệnh từ CRM", get_commands_action)
        ]

        # Random hóa thứ tự các hành động
        random.shuffle(actions)
        
        # Check interrupt trước khi bắt đầu
        if stop_event and stop_event.is_set():
            log_message("Facebook natural task interrupted before start", logging.INFO)
            return
            
        if pause_event and pause_event.is_set():
            log_message("Facebook natural task paused before start", logging.INFO)
            if resume_event:
                await resume_event.wait()

        log_message(f"\n\n{driver.serial} Thực hiện tác vụ: Xem reels\n")

        # Xem reels với interrupt support
        log_message(f"[{driver.serial}] Starting watch_reels with interrupt support")
        await run_task_with_interrupt(watch_reels, driver, stop_event, pause_event, resume_event)
        
        # Check interrupt sau khi xem reels
        if stop_event and stop_event.is_set():
            log_message("Facebook natural task interrupted after watch_reels", logging.INFO)
            return
            
        await interruptible_sleep(random.uniform(4,6), stop_event, pause_event, resume_event)

        # Thực hiện các action khác với interrupt checks
        for name, action in actions:
            # Check interrupt trước mỗi action
            if stop_event and stop_event.is_set():
                log_message(f"Facebook natural task interrupted before {name}", logging.INFO)
                return
                
            if pause_event and pause_event.is_set():
                log_message(f"Facebook natural task paused before {name}", logging.INFO)
                if resume_event:
                    await resume_event.wait()
                log_message(f"Facebook natural task resumed, continuing with {name}", logging.INFO)

            log_message(f"\n\n{driver.serial} Thực hiện tác vụ: {name}\n", logging.INFO)

            # Chạy action trực tiếp vì giờ đây chúng đều là async functions
            try:
                await action()
            except Exception as e:
                if stop_event and stop_event.is_set():
                    log_message(f"Action {name} interrupted: {e}", logging.INFO)
                    return
                else:
                    log_message(f"Error in action {name}: {e}", logging.ERROR)
                    # Tiếp tục với action khác
            
            # Check interrupt sau mỗi action
            if stop_event and stop_event.is_set():
                log_message(f"Facebook natural task interrupted after {name}", logging.INFO)
                return

            await interruptible_sleep(random.uniform(4,6), stop_event, pause_event, resume_event)

        log_message(f"{driver.serial} Hoàn thành 1 chuỗi task với interrupt support")
        
    except Exception as e:
        if stop_event and stop_event.is_set():
            log_message(f"Facebook natural task interrupted: {e}", logging.INFO)
        else:
            log_message(f"Error in fb_natural_task_interruptible: {e}", logging.ERROR)

# Backward compatibility - original function without interrupt
async def run_on_device_original(driver):
    try:
        device_id = driver.serial

        # await clear_app(driver)
        driver.press("home")
        driver.app_start("com.facebook.katana", ".LoginActivity")
        await asyncio.sleep(random.uniform(10,15))

        device = load_device_account(device_id)
        if not device:
            log_message(f"Không tìm thấy dữ liệu cho thiết bị {device_id}", logging.WARNING)
            emp_id = "22615833"
            account = "default"
        else:
            emp_id = device['user']['emp_id']
            # Chuyển tài khoản
            last_time = device['time_logged_in']
            if last_time and (datetime.fromisoformat(last_time) + timedelta(hours=random.randint(4,6))) < datetime.now():
                # Đủ thời gian, chuyển tài khoản
                i=0
                for acc in device['accounts']:
                    i+=1
                    if acc['account'] == device['current_account']:
                        break
                if i==3: i=0
                for acc in device['accounts']:
                    if i==0:
                        device['current_account'] = acc['account']
                        break
                    i-=1
                log_message(f"Đang đăng nhập vào tài khoản {account['name']} trên thiết bị {device_id}")
                await swap_account(driver, account)
                device['current_account'] = account['account']
                update_current_account(device_id, account)
            account = device['current_account']
        # tasks nuôi fb
        await fb_natural_task(driver, emp_id, account)
        # await share_post(driver, text=random.choice(SHARES))
    except Exception as e:
        log_message(f"Lỗi trên thiết bị {device_id}: {e}", logging.ERROR)