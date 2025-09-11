import uiautomator2 as u2
from module import *
import subprocess
import asyncio
import time
import json
# import mapping nếu cần thiết sau

async def run_adb_devices_loop():
    """
    Chạy lệnh adb devices mỗi 2 giây
    """
    print("Bắt đầu monitor adb devices...")
    
    while True:
        try:
            # Chạy lệnh adb devices
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            # In kết quả với timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] ADB Devices:")
            print(result.stdout)
            
            if result.stderr:
                print(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("ADB command timeout!")
        except FileNotFoundError:
            print("ADB not found! Vui lòng kiểm tra PATH hoặc cài đặt ADB.")
            break
        except Exception as e:
            print(f"Error running adb devices: {e}")
        
        # Đợi 2 giây
        await asyncio.sleep(2)

def run_adb_devices_sync():
    """
    Phiên bản synchronous của hàm monitor adb devices
    """
    print("Bắt đầu monitor adb devices (sync)...")
    
    while True:
        try:
            # Chạy lệnh adb devices
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            # In kết quả với timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] ADB Devices:")
            print(result.stdout)
            
            if result.stderr:
                print(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("ADB command timeout!")
        except FileNotFoundError:
            print("ADB not found! Vui lòng kiểm tra PATH hoặc cài đặt ADB.")
            break
        except KeyboardInterrupt:
            print("\nDừng monitor adb devices.")
            break
        except Exception as e:
            print(f"Error running adb devices: {e}")
        
        # Đợi 2 giây
        time.sleep(2)

# ======================= TEST AUTO ROTATION =======================

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

def get_connected_devices():
    """Lấy danh sách devices đang kết nối"""
    try:
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # Bỏ dòng đầu "List of devices attached"
        
        for line in lines:
            if line.strip() and 'device' in line:
                device_id = line.split()[0]
                devices.append(device_id)
        
        return devices
    except Exception as e:
        print(f"Lỗi lấy danh sách devices: {e}")
        return []

async def check_single_device_auto_rotation(device_id: str):
    """Kiểm tra trạng thái auto rotation của 1 device"""
    try:
        print(f"\n🔍 Kiểm tra device: {device_id}")
        
        # Kết nối device
        driver = u2.connect_usb(device_id)
        
        # Kiểm tra kết nối
        try:
            info = driver.info
            print(f"  ✅ Kết nối thành công: {info.get('productName', 'Unknown')} - Android {info.get('version', 'Unknown')}")
        except Exception as e:
            print(f"  ❌ Không thể lấy thông tin device: {e}")
            return None
        
        # Kiểm tra trạng thái auto rotation
        try:
            result = driver.shell("settings get system accelerometer_rotation")
            auto_rotation_value = parse_shell_response(result)
            auto_rotation_status = "BẬT" if auto_rotation_value == "1" else "TẮT" if auto_rotation_value == "0" else "KHÔNG XÁC ĐỊNH"
            
            print(f"  🔄 Auto-rotation: {auto_rotation_status} (value: {auto_rotation_value})")
            
        except Exception as e:
            print(f"  ❌ Không thể kiểm tra auto-rotation: {e}")
            auto_rotation_status = "LỖI"
            auto_rotation_value = "N/A"
        
        # Kiểm tra orientation hiện tại
        try:
            display_info = driver.info
            current_orientation = display_info.get('displayRotation', 'Unknown')
            orientation_map = {0: "Portrait", 1: "Landscape (Left)", 2: "Portrait (Upside Down)", 3: "Landscape (Right)"}
            orientation_name = orientation_map.get(current_orientation, f"Unknown ({current_orientation})")
            
            print(f"  📱 Orientation hiện tại: {orientation_name}")
            
        except Exception as e:
            print(f"  ❌ Không thể kiểm tra orientation: {e}")
            current_orientation = "N/A"
            orientation_name = "N/A"
        
        # Kiểm tra màn hình size
        try:
            width, height = driver.window_size()
            print(f"  📐 Kích thước màn hình: {width}x{height}")
            
        except Exception as e:
            print(f"  ❌ Không thể lấy kích thước màn hình: {e}")
            width, height = "N/A", "N/A"
        
        # Trả về kết quả
        return {
            "device_id": device_id,
            "connection": "success",
            "auto_rotation": {
                "status": auto_rotation_status,
                "value": auto_rotation_value
            },
            "orientation": {
                "current": current_orientation,
                "name": orientation_name
            },
            "screen_size": f"{width}x{height}",
            "device_info": info if 'info' in locals() else None
        }
        
    except Exception as e:
        print(f"  ❌ Lỗi kiểm tra device {device_id}: {e}")
        return {
            "device_id": device_id,
            "connection": "failed",
            "error": str(e)
        }

async def disable_all_auto_rotation():
    """Tắt auto rotation cho tất cả devices trước khi test"""
    print("🔧 BẮT ĐẦU TẮT AUTO ROTATION CHO TẤT CẢ DEVICES")
    print("=" * 60)
    
    connected_devices = get_connected_devices()
    
    if not connected_devices:
        print("❌ Không tìm thấy device nào!")
        return
    
    print(f"📱 Tìm thấy {len(connected_devices)} device(s), tiến hành tắt auto-rotation...")
    
    success_count = 0
    failed_count = 0
    
    for device_id in connected_devices:
        try:
            print(f"\n🔍 Xử lý device: {device_id}")
            
            driver = u2.connect_usb(device_id)
            
            # Kiểm tra trạng thái hiện tại
            result = driver.shell("settings get system accelerometer_rotation")
            current_value = parse_shell_response(result)
            
            if current_value == "1":
                print(f"  🔴 Auto-rotation đang BẬT - Tiến hành TẮT...")
                
                # Tắt auto-rotation
                driver.shell("settings put system accelerometer_rotation 0")
                await asyncio.sleep(0.5)  # Chờ ngắn để settings apply
                
                # Kiểm tra lại
                new_result = driver.shell("settings get system accelerometer_rotation")
                new_value = parse_shell_response(new_result)
                
                if new_value == "0":
                    print(f"  ✅ Đã TẮT auto-rotation thành công!")
                    success_count += 1
                else:
                    print(f"  ❌ Không thể tắt auto-rotation (value: {new_value})")
                    failed_count += 1
                    
            elif current_value == "0":
                print(f"  🟢 Auto-rotation đã TẮT - OK!")
                success_count += 1
            else:
                print(f"  ⚪ Trạng thái không xác định (value: {current_value})")
                failed_count += 1
            
        except Exception as e:
            print(f"  ❌ Lỗi xử lý device {device_id}: {e}")
            failed_count += 1
    
    print(f"\n" + "=" * 60)
    print(f"📊 KẾT QUẢ TẮT AUTO-ROTATION:")
    print(f"  ✅ Thành công: {success_count}/{len(connected_devices)} devices")
    print(f"  ❌ Thất bại: {failed_count}/{len(connected_devices)} devices")
    
    if failed_count == 0:
        print(f"\n🎉 TẤT CẢ DEVICES ĐÃ TẮT AUTO-ROTATION!")
    else:
        print(f"\n⚠️  Có {failed_count} device(s) không thể tắt auto-rotation")

async def disable_auto_rotation_then_test():
    """Tắt auto rotation trước, sau đó test tất cả devices"""
    print("🚀 TẮT AUTO-ROTATION VÀ KIỂM TRA TẤT CẢ DEVICES")
    print("=" * 60)
    
    # Bước 1: Tắt hết auto-rotation
    await disable_all_auto_rotation()
    
    # Chờ 2 giây cho settings apply
    print(f"\n⏳ Chờ 2 giây để settings áp dụng...")
    await asyncio.sleep(2)
    
    # Bước 2: Test lại tất cả
    print(f"\n🔍 KIỂM TRA LẠI TRẠNG THÁI SAU KHI TẮT:")
    print("=" * 60)
    await test_all_devices_auto_rotation()

async def test_all_devices_auto_rotation():
    """Test trạng thái auto rotation của tất cả devices"""
    print("🚀 BẮT ĐẦU TEST AUTO ROTATION CHO TẤT CẢ DEVICES")
    print("=" * 60)
    
    # Lấy danh sách devices
    connected_devices = get_connected_devices()
    
    if not connected_devices:
        print("❌ Không tìm thấy device nào được kết nối!")
        return
    
    print(f"📱 Tìm thấy {len(connected_devices)} device(s) được kết nối:")
    for device in connected_devices:
        print(f"  - {device}")
    
    print("\n" + "=" * 60)
    
    # Test từng device
    results = []
    for device_id in connected_devices:
        try:
            result = await check_single_device_auto_rotation(device_id)
            results.append(result)
            await asyncio.sleep(1)  # Chờ giữa các device để tránh conflict
            
        except Exception as e:
            print(f"❌ Lỗi test device {device_id}: {e}")
            results.append({
                "device_id": device_id,
                "connection": "error",
                "error": str(e)
            })
    
    # Tổng kết
    print("\n" + "=" * 60)
    print("📊 TỔNG KẾT KẾT QUẢ:")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r and r.get("connection") == "success")
    failed_count = len(results) - success_count
    
    print(f"✅ Thành công: {success_count}/{len(results)} devices")
    print(f"❌ Thất bại: {failed_count}/{len(results)} devices")
    
    # Chi tiết kết quả
    auto_rotation_on = 0
    auto_rotation_off = 0
    
    for result in results:
        if result and result.get("connection") == "success":
            device_id = result["device_id"]
            auto_status = result["auto_rotation"]["status"]
            orientation = result["orientation"]["name"]
            screen_size = result["screen_size"]
            
            status_icon = "🟢" if auto_status == "TẮT" else "🔴" if auto_status == "BẬT" else "⚪"
            print(f"\n{status_icon} {device_id}:")
            print(f"    Auto-rotation: {auto_status}")
            print(f"    Orientation: {orientation}")
            print(f"    Screen: {screen_size}")
            
            if auto_status == "BẬT":
                auto_rotation_on += 1
            elif auto_status == "TẮT":
                auto_rotation_off += 1
    
    print(f"\n📈 THỐNG KÊ AUTO-ROTATION:")
    print(f"  🔴 BẬT: {auto_rotation_on} devices")
    print(f"  🟢 TẮT: {auto_rotation_off} devices")
    
    # Lưu kết quả ra file JSON
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"auto_rotation_test_result_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_devices": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "auto_rotation_stats": {
                    "on": auto_rotation_on,
                    "off": auto_rotation_off
                },
                "detailed_results": results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Kết quả đã được lưu vào file: {filename}")
        
    except Exception as e:
        print(f"\n❌ Lỗi lưu file kết quả: {e}")

async def test_and_fix_auto_rotation():
    """Test và tự động sửa auto rotation nếu cần"""
    print("🔧 BẮT ĐẦU TEST VÀ SỬA AUTO ROTATION")
    print("=" * 60)
    
    connected_devices = get_connected_devices()
    
    if not connected_devices:
        print("❌ Không tìm thấy device nào!")
        return
    
    for device_id in connected_devices:
        try:
            print(f"\n🔍 Xử lý device: {device_id}")
            
            driver = u2.connect_usb(device_id)
            
            # Kiểm tra trạng thái hiện tại
            result = driver.shell("settings get system accelerometer_rotation")
            current_value = parse_shell_response(result)
            
            if current_value == "1":
                print(f"  🔴 Auto-rotation đang BẬT - Tiến hành TẮT...")
                
                # Tắt auto-rotation
                driver.shell("settings put system accelerometer_rotation 0")
                await asyncio.sleep(1)
                
                # Kiểm tra lại
                new_result = driver.shell("settings get system accelerometer_rotation")
                new_value = parse_shell_response(new_result)
                
                if new_value == "0":
                    print(f"  ✅ Đã TẮT auto-rotation thành công!")
                else:
                    print(f"  ❌ Không thể tắt auto-rotation (value: {new_value})")
                    
            elif current_value == "0":
                print(f"  🟢 Auto-rotation đã TẮT - OK!")
            else:
                print(f"  ⚪ Trạng thái không xác định (value: {current_value})")
            
        except Exception as e:
            print(f"  ❌ Lỗi xử lý device {device_id}: {e}")

# Chạy hàm async
async def main():
    print("Chọn chức năng:")
    print("1. Monitor ADB devices")
    print("2. Test auto rotation tất cả devices")
    print("3. Test và sửa auto rotation") 
    print("4. Test 1 device cụ thể")
    print("5. TẮT auto rotation tất cả devices trước khi test")
    print("6. Chỉ TẮT auto rotation (không test)")
    
    choice = input("Nhập lựa chọn (1-6): ").strip()
    
    if choice == "1":
        await run_adb_devices_loop()
    elif choice == "2":
        await test_all_devices_auto_rotation()
    elif choice == "3":
        await test_and_fix_auto_rotation()
    elif choice == "4":
        device_id = input("Nhập Device ID: ").strip()
        if device_id:
            await check_single_device_auto_rotation(device_id)
        else:
            print("Device ID không hợp lệ!")
    elif choice == "5":
        await disable_auto_rotation_then_test()
    elif choice == "6":
        await disable_all_auto_rotation()
    else:
        print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    # Có thể chọn 1 trong 2 cách:
    
    # Cách 1: Chạy async
    print("Chạy test auto rotation...")
    asyncio.run(main())
    
    # Cách 2: Chạy sync (uncomment để sử dụng)
    # print("Chạy sync version...")
    # run_adb_devices_sync()


