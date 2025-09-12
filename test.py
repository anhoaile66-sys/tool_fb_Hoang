import json
import asyncio

device_id = "QK8TEMKZMBYHPV6P"
status = False

async def gia_lap_task_60s():
    global status
    status = True
    for i in range(60):
        await asyncio.sleep(1)
        print(f"Task running {i+1}/60")
    print("Task 60s completed")
    status = False

async def main_loop():
    global status
    task = asyncio.create_task(gia_lap_task_60s())

    while True:
        try:
            while True:
                is_paused = False
                device_status_path = f"Zalo_base/device_status_{device_id}.json"
                try:
                    with open(device_status_path, 'r', encoding='utf-8') as f:
                        device_status = json.load(f)
                    if device_status.get('active', False):
                        is_paused = True
                except Exception:
                    pass

                if is_paused:
                    if not task.done():
                        task.cancel()
                        print("Task đã bị hủy do thiết bị active")
                    status = False
                    await asyncio.sleep(0.1)
                else:
                    break

            if not status:
                task = asyncio.create_task(gia_lap_task_60s())

            await asyncio.sleep(0.5)  # Cho vòng lặp chính không bị quá nhanh

        except KeyboardInterrupt:
            print("Đã dừng bằng tay.")
            break
        except Exception as e:
            print(f"Lỗi trong vòng lặp chính: {e}")
            await asyncio.sleep(5)

# Chạy chương trình
asyncio.run(main_loop())