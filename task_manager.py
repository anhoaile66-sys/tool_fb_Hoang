import asyncio
import logging
import time
import json
from typing import Dict, Callable, Optional, Any
from enum import Enum
from dataclasses import dataclass
from collections import deque
import threading

# Import log_message
try:
    from util.log import log_message
except ImportError:
    def log_message(msg: str, level=logging.INFO):
        print(f"[{level}] {msg}")

class TaskPriority(Enum):
    """Độ ưu tiên task"""
    LOW = 1          # Task thường (lướt FB, xem video)
    NORMAL = 2       # Task bình thường 
    HIGH = 3         # Task quan trọng từ server
    URGENT = 4       # Task khẩn cấp (phải làm ngay)

class TaskStatus(Enum):
    """Trạng thái task"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class Task:
    """Đại diện cho một task"""
    id: str
    name: str
    priority: TaskPriority
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = 0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    device_id: Optional[str] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.created_at == 0:
            self.created_at = time.time()

class InterruptibleTask:
    """Wrapper cho task có thể bị interrupt"""
    def __init__(self, task: Task):
        self.task = task
        self.stop_event = asyncio.Event()
        self.pause_event = asyncio.Event()
        self.resume_event = asyncio.Event()
        self.resume_event.set()  # Mặc định không bị pause
        
    async def run(self):
        """Chạy task với khả năng interrupt"""
        self.task.status = TaskStatus.RUNNING
        self.task.started_at = time.time()
        
        try:
            # Truyền control events vào task function
            if asyncio.iscoroutinefunction(self.task.func):
                result = await self.task.func(
                    *self.task.args,
                    stop_event=self.stop_event,
                    pause_event=self.pause_event,
                    resume_event=self.resume_event,
                    **self.task.kwargs
                )
            else:
                result = await asyncio.to_thread(
                    self.task.func,
                    *self.task.args,
                    **self.task.kwargs
                )
            
            if not self.stop_event.is_set():
                self.task.status = TaskStatus.COMPLETED
                self.task.completed_at = time.time()
            else:
                self.task.status = TaskStatus.CANCELLED
                
            return result
            
        except Exception as e:
            self.task.status = TaskStatus.FAILED
            log_message(f"Task {self.task.id} failed: {e}", logging.ERROR)
            raise
    
    def stop(self):
        """Dừng task"""
        self.stop_event.set()
        self.resume()  # Đảm bảo task không bị pause khi stop
        
    def pause(self):
        """Tạm dừng task"""
        self.task.status = TaskStatus.PAUSED
        self.resume_event.clear()
        self.pause_event.set()
        
    def resume(self):
        """Tiếp tục task"""
        if self.task.status == TaskStatus.PAUSED:
            self.task.status = TaskStatus.RUNNING
        self.pause_event.clear()
        self.resume_event.set()

class TaskManager:
    """Quản lý task với priority và interrupt"""
    
    def __init__(self):
        self.tasks: Dict[str, InterruptibleTask] = {}
        self.device_tasks: Dict[str, str] = {}  # device_id -> current_task_id
        self.task_queue = deque()
        self.running = False
        self.websocket_client = None
        
    async def add_task(self, task: Task) -> str:
        """Thêm task mới"""
        interruptible_task = InterruptibleTask(task)
        self.tasks[task.id] = interruptible_task
        
        # Nếu là task priority cao và có device đang chạy task priority thấp
        if task.device_id and task.priority.value >= TaskPriority.HIGH.value:
            current_task_id = self.device_tasks.get(task.device_id)
            if current_task_id and current_task_id in self.tasks:
                current_task = self.tasks[current_task_id]
                if current_task.task.priority.value < task.priority.value:
                    log_message(f"Interrupting lower priority task {current_task_id} for {task.id}")
                    current_task.pause()
        
        # Thêm vào queue theo priority
        self._insert_by_priority(task.id)
        
        log_message(f"Added task {task.id} ({task.name}) with priority {task.priority.name}")
        return task.id
    
    def _insert_by_priority(self, task_id: str):
        """Chèn task vào queue theo priority"""
        task = self.tasks[task_id].task
        inserted = False
        
        for i, existing_task_id in enumerate(self.task_queue):
            existing_task = self.tasks[existing_task_id].task
            if task.priority.value > existing_task.priority.value:
                self.task_queue.insert(i, task_id)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task_id)
    
    async def run_task_queue(self):
        """Chạy task queue"""
        self.running = True
        
        while self.running:
            if not self.task_queue:
                await asyncio.sleep(1)
                continue
            
            task_id = self.task_queue.popleft()
            if task_id not in self.tasks:
                continue
                
            interruptible_task = self.tasks[task_id]
            task = interruptible_task.task
            
            # Kiểm tra xem device có đang busy không
            if task.device_id:
                current_task_id = self.device_tasks.get(task.device_id)
                if current_task_id and current_task_id != task_id:
                    current_task = self.tasks[current_task_id]
                    if current_task.task.status == TaskStatus.RUNNING:
                        # Nếu task mới có priority cao hơn
                        if task.priority.value > current_task.task.priority.value:
                            log_message(f"Pausing task {current_task_id} for higher priority task {task_id}")
                            current_task.pause()
                        else:
                            # Task priority thấp hơn, quay lại queue
                            self.task_queue.appendleft(task_id)
                            await asyncio.sleep(2)
                            continue
                
                self.device_tasks[task.device_id] = task_id
            
            try:
                log_message(f"Starting task {task_id} ({task.name}) on device {task.device_id}")
                await interruptible_task.run()
                log_message(f"Completed task {task_id}")
                
            except Exception as e:
                log_message(f"Task {task_id} failed: {e}", logging.ERROR)
            
            finally:
                # Cleanup
                if task.device_id and self.device_tasks.get(task.device_id) == task_id:
                    del self.device_tasks[task.device_id]
                
                # Resume paused tasks cho device này
                await self._resume_paused_tasks(task.device_id)
    
    async def _resume_paused_tasks(self, device_id: str):
        """Resume các task bị pause cho device"""
        for task_id, interruptible_task in self.tasks.items():
            if (interruptible_task.task.device_id == device_id and 
                interruptible_task.task.status == TaskStatus.PAUSED):
                log_message(f"Resuming paused task {task_id}")
                interruptible_task.resume()
                self._insert_by_priority(task_id)
                break
    
    async def stop_all_tasks(self, device_id: str = None):
        """Dừng tất cả task hoặc task của device cụ thể"""
        for task_id, interruptible_task in self.tasks.items():
            if device_id is None or interruptible_task.task.device_id == device_id:
                interruptible_task.stop()
        
        if device_id and device_id in self.device_tasks:
            del self.device_tasks[device_id]
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Lấy trạng thái task"""
        if task_id in self.tasks:
            return self.tasks[task_id].task.status
        return None
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Lấy trạng thái device"""
        current_task_id = self.device_tasks.get(device_id)
        status = {
            "device_id": device_id,
            "current_task": None,
            "queue_length": 0
        }
        
        if current_task_id and current_task_id in self.tasks:
            task = self.tasks[current_task_id].task
            status["current_task"] = {
                "id": task.id,
                "name": task.name,
                "priority": task.priority.name,
                "status": task.status.value,
                "started_at": task.started_at
            }
        
        # Đếm task trong queue cho device này
        queue_count = sum(1 for tid in self.task_queue 
                         if tid in self.tasks and self.tasks[tid].task.device_id == device_id)
        status["queue_length"] = queue_count
        
        return status

# Global task manager instance
task_manager = TaskManager()

async def start_task_manager():
    """Khởi động task manager"""
    log_message("Starting Task Manager...")
    await task_manager.run_task_queue()

# Helper functions để tạo task dễ dàng
async def create_facebook_task(device_id: str, priority: TaskPriority = TaskPriority.LOW) -> str:
    """Tạo task chạy Facebook"""
    from fb_task import run_on_device
    import uiautomator2 as u2
    
    async def facebook_task_wrapper(stop_event, pause_event, resume_event):
        driver = await asyncio.to_thread(u2.connect_usb, device_id)
        
        # Wrapper cho run_on_device với interrupt support
        async def interruptible_run_on_device():
            # Chia nhỏ task và check interrupt
            try:
                await run_on_device(driver)
            except Exception as e:
                if not stop_event.is_set():
                    raise e
        
        await interruptible_run_on_device()
    
    task = Task(
        id=f"facebook_{device_id}_{int(time.time())}",
        name=f"Facebook browsing on {device_id}",
        priority=priority,
        func=facebook_task_wrapper,
        device_id=device_id
    )
    
    return await task_manager.add_task(task)

async def create_server_task(device_id: str, action: str, content: str) -> str:
    """Tạo task từ server request"""
    print(action)
    
    async def server_task_wrapper(stop_event, pause_event, resume_event, **kwargs):
        # Lấy content từ kwargs hoặc sử dụng giá trị từ closure
        task_content = kwargs.get('content', content) or ""
        
        # Implement server tasks here
        log_message(f"Executing server task: {action} on {device_id} with content: {task_content[:50]}...")
        
        if action == "post_content":
            log_message(f"Posting content: {task_content[:50]}...")
            # TODO: Implement actual post content logic
            # Go to home page trước khi đếm
            try:
                import uiautomator2 as u2
                driver = u2.connect_usb(device_id)
                driver.press("home")
                log_message(f"[{device_id}] Pressed home button before counting")
                await asyncio.sleep(2)  # Đợi home page load
            except Exception as e:
                log_message(f"[{device_id}] Error going to home: {e}", logging.ERROR)

            for _ in range(50):
                print("Đếm số: ", _)
                await asyncio.sleep(1)

            
        elif action == "send_message":
            # Parse content string để lấy recipient và message
            try:
                parts = task_content.split(';')
                recipient = parts[0].split(':')[1] if len(parts) > 0 and ':' in parts[0] else ""
                message = parts[1].split(':')[1] if len(parts) > 1 and ':' in parts[1] else ""
                log_message(f"Sending message to {recipient}: {message[:30]}...")
            except Exception as e:
                log_message(f"Error parsing send_message content: {e}", logging.ERROR)
                log_message(f"Raw content: {task_content}")
            # TODO: Implement actual send message logic
            await asyncio.sleep(3)  # Simulate work
            
        elif action == "add_friend":
            log_message(f"Adding friend: {task_content}")
            # TODO: Implement actual add friend logic
            await asyncio.sleep(2)  # Simulate work
        
        # Luôn check stop_event trong quá trình làm việc
        if stop_event and stop_event.is_set():
            log_message(f"Server task {action} was interrupted")
            return
        
        log_message(f"Server task {action} completed successfully")
    
    task = Task(
        id=f"server_{action}_{device_id}_{int(time.time())}",
        name=f"Server task: {action}",
        priority=TaskPriority.HIGH,  # Server task có priority cao
        func=server_task_wrapper,
        device_id=device_id,
        kwargs={"content": content}  # Truyền content qua kwargs
    )
    
    return await task_manager.add_task(task)
