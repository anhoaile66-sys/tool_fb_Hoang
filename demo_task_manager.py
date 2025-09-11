"""
Demo script để test Task Manager với WebSocket integration

Cách test:
1. Chạy script này
2. Gửi message từ server WebSocket để test interrupt
3. Quan sát log để thấy task bị interrupt và resume

Example WebSocket messages để test:
{
    "type": "new_post",
    "device_id": "test_device",
    "content": "Hello from server!"
}

{
    "type": "stop_device", 
    "device_id": "test_device"
}

{
    "type": "get_status",
    "device_id": "test_device"
}
"""

import asyncio
import logging
import time
from task_manager import (
    task_manager, 
    Task, 
    TaskPriority, 
    create_facebook_task,
    create_server_task
)
from module.websocket import start_websocket_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def mock_facebook_task(device_id: str, stop_event=None, pause_event=None, resume_event=None):
    """Mock Facebook task để test interrupt"""
    print(f"🔵 [MockFB] Starting Facebook browsing on {device_id}")
    
    try:
        for i in range(20):  # Simulate 20 minutes of browsing
            # Check stop
            if stop_event and stop_event.is_set():
                print(f"🔴 [MockFB] Facebook task stopped on {device_id}")
                return
            
            # Check pause
            if pause_event and pause_event.is_set():
                print(f"⏸️ [MockFB] Facebook task paused on {device_id}")
                if resume_event:
                    await resume_event.wait()
                print(f"▶️ [MockFB] Facebook task resumed on {device_id}")
            
            print(f"📱 [MockFB] Browsing Facebook... step {i+1}/20 on {device_id}")
            await asyncio.sleep(3)  # 3 seconds per step = 1 minute total
        
        print(f"✅ [MockFB] Facebook task completed on {device_id}")
        
    except Exception as e:
        print(f"❌ [MockFB] Facebook task error on {device_id}: {e}")

async def mock_server_task(action: str, device_id: str, params: dict, stop_event=None, pause_event=None, resume_event=None):
    """Mock server task để test priority"""
    print(f"🟡 [Server] Starting {action} on {device_id} with params: {params}")
    
    try:
        # Simulate server task work
        if action == "post_content":
            print(f"📝 [Server] Posting content: {params.get('content', '')[:30]}...")
            await asyncio.sleep(5)
            
        elif action == "send_message":
            print(f"💬 [Server] Sending message to {params.get('recipient', 'unknown')}")
            await asyncio.sleep(3)
            
        elif action == "add_friend":
            print(f"👥 [Server] Adding friend: {params.get('user_id', 'unknown')}")
            await asyncio.sleep(2)
        
        print(f"✅ [Server] {action} completed on {device_id}")
        
    except Exception as e:
        print(f"❌ [Server] {action} error on {device_id}: {e}")

async def create_mock_facebook_task(device_id: str, priority: TaskPriority = TaskPriority.LOW) -> str:
    """Tạo mock Facebook task"""
    task = Task(
        id=f"mock_facebook_{device_id}_{int(time.time())}",
        name=f"Mock Facebook browsing on {device_id}",
        priority=priority,
        func=mock_facebook_task,
        args=(device_id,),
        device_id=device_id
    )
    
    return await task_manager.add_task(task)

async def create_mock_server_task(device_id: str, action: str, params: dict = None) -> str:
    """Tạo mock server task"""
    if params is None:
        params = {}
        
    task = Task(
        id=f"mock_server_{action}_{device_id}_{int(time.time())}",
        name=f"Mock Server task: {action}",
        priority=TaskPriority.HIGH,
        func=mock_server_task,
        args=(action, device_id, params),
        device_id=device_id
    )
    
    return await task_manager.add_task(task)

async def demo_task_interruption():
    """Demo task interruption scenario"""
    print("🚀 Starting Task Manager Demo...")
    
    # Start task manager
    asyncio.create_task(task_manager.run_task_queue())
    await asyncio.sleep(1)
    
    # Device to test
    test_device = "demo_device_001"
    
    print(f"📱 Creating long-running Facebook task on {test_device}")
    fb_task_id = await create_mock_facebook_task(test_device, TaskPriority.LOW)
    
    # Let it run for a bit
    await asyncio.sleep(10)
    
    print("🔥 Server sends high priority task - should interrupt Facebook!")
    server_task_id = await create_mock_server_task(
        test_device,
        "post_content", 
        {"content": "Urgent post from server!"}
    )
    
    # Wait for server task to complete
    await asyncio.sleep(8)
    
    print("📊 Checking device status...")
    status = task_manager.get_device_status(test_device)
    print(f"Device Status: {status}")
    
    # Wait a bit more to see resumption
    await asyncio.sleep(15)
    
    print("🏁 Demo completed!")

async def demo_multiple_devices():
    """Demo với nhiều device"""
    print("🚀 Starting Multi-Device Demo...")
    
    # Start task manager
    asyncio.create_task(task_manager.run_task_queue())
    await asyncio.sleep(1)
    
    devices = ["device_A", "device_B", "device_C"]
    
    # Create Facebook tasks for all devices
    for device in devices:
        await create_mock_facebook_task(device, TaskPriority.LOW)
        await asyncio.sleep(1)
    
    await asyncio.sleep(5)
    
    # Create server tasks for some devices
    await create_mock_server_task("device_A", "send_message", {"recipient": "user123"})
    await asyncio.sleep(2)
    await create_mock_server_task("device_C", "add_friend", {"user_id": "friend456"})
    
    # Monitor for a while
    for i in range(10):
        await asyncio.sleep(3)
        for device in devices:
            status = task_manager.get_device_status(device)
            current_task = status.get("current_task", {})
            if current_task:
                print(f"📱 {device}: {current_task.get('name', 'No task')} ({current_task.get('status', 'unknown')})")

async def main():
    """Main demo function"""
    print("=" * 60)
    print("🎯 TASK MANAGER + WEBSOCKET INTEGRATION DEMO")
    print("=" * 60)
    
    choice = input("""
Choose demo:
1. Task Interruption Demo (recommended)
2. Multiple Devices Demo  
3. WebSocket + Task Manager (needs WebSocket server)

Enter choice (1-3): """).strip()
    
    if choice == "1":
        await demo_task_interruption()
    elif choice == "2":
        await demo_multiple_devices()
    elif choice == "3":
        print("🌐 Starting WebSocket + Task Manager integration...")
        print("📡 Make sure your WebSocket server is running on ws://192.168.0.89:4000")
        
        # Start task manager
        asyncio.create_task(task_manager.run_task_queue())
        
        # Start websocket client (this will run indefinitely)
        await start_websocket_client("demo_client")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
