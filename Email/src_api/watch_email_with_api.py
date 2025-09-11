import time
import os
import sqlite3
from datetime import datetime
from classSend import EmailSender
from classHtmlRender import HtmlRenderSimulator

# --- Cấu hình ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "business", "businesses.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_distinct_emp_ids_with_pending_emails():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT emp_id FROM customers WHERE sent = 0"
    )
    emp_ids = [row["emp_id"] for row in cursor.fetchall()]
    conn.close()
    return emp_ids

def get_next_pending_customer(emp_id):
    """Lấy khách hàng chờ xử lý tiếp theo cho một emp_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_id FROM customers WHERE emp_id = ? AND sent = 0 ORDER BY customer_id LIMIT 1",
        (emp_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result["customer_id"] if result else None

def is_customer_sent(customer_id):
    """Kiểm tra xem một customer đã được đánh dấu là đã gửi chưa."""
    if customer_id is None:
        return True # Không có customer trước đó, coi như đã xử lý
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sent FROM customers WHERE customer_id = ?",
        (customer_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result["sent"] == 1 if result else False

def process_emails_for_emp(emp_id):
    print(f"👂 Bắt đầu xử lý cho EMP_ID: {emp_id}...")
    
    last_customer_id_processed = None
    html_processed_successfully = True

    while True:
        # Điều kiện để xử lý hàng tiếp theo:
        # 1. DB của hàng trước đó đã được cập nhật là sent=1
        # 2. HTML của hàng trước đó đã được xử lý thành công
        if not is_customer_sent(last_customer_id_processed) or not html_processed_successfully:
            print(f"🔴 Hàng trước đó (ID: {last_customer_id_processed}) chưa được xử lý xong. Tạm dừng cho EMP_ID: {emp_id}.")
            break

        customer_id = get_next_pending_customer(emp_id)

        if customer_id is None:
            print(f"✅ Không còn khách hàng nào chờ xử lý cho EMP_ID: {emp_id}.")
            break
        
        print(f"\n▶️ Đang xử lý khách hàng ID: {customer_id}...")

        try:
            # 1. Xử lý HTML
            print("   - Bước 1: Xử lý HTML...")
            simulator = HtmlRenderSimulator(EMP_ID=emp_id, customer_id=customer_id)
            simulator.beautify_html()
            
            html_processed_successfully = simulator.html_processed
            if not html_processed_successfully:
                print(f"   - ❌ Lỗi: Xử lý HTML thất bại cho customer ID: {customer_id}.")
                # Dừng vòng lặp, lần check sau sẽ bị chặn lại ở điều kiện đầu
                continue 
            print("   - ✅ HTML đã được xử lý.")

            # 2. Gửi email
            print("   - Bước 2: Gửi email...")
            sender = EmailSender(emp_id=emp_id)
            # Không cần mở Gmail mỗi lần nếu app đã mở, nhưng để đơn giản, ta giữ nguyên
            sender.open_gmail() 
            success = sender.send_to_customer(customer_id)

            if success:
                print(f"   - ✅ Gửi email thành công cho customer ID: {customer_id}.")
                last_customer_id_processed = customer_id
            else:
                print(f"   - ❌ Lỗi: Gửi email thất bại cho customer ID: {customer_id}.")
                # Dừng xử lý cho emp_id này, vì gửi lỗi
                break
        
        except Exception as e:
            print(f"   - ❌ Đã xảy ra lỗi nghiêm trọng khi xử lý customer ID {customer_id}: {e}")
            # Dừng xử lý cho emp_id này
            break
        
        # Nghỉ một chút trước khi xử lý khách hàng tiếp theo
        time.sleep(5)


def main():
    while True:
        print(f"\n--- Chạy kiểm tra lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        emp_ids = get_distinct_emp_ids_with_pending_emails()
        
        if not emp_ids:
            print("ℹ️ Không có nhân viên nào có email cần gửi.")
        else:
            print(f"🔍 Tìm thấy {len(emp_ids)} nhân viên có email chờ xử lý: {emp_ids}")
            for emp_id in emp_ids:
                process_emails_for_emp(emp_id)
        
        print(f"--- Hoàn thành chu kỳ, nghỉ 300 giây ---")
        time.sleep(300)

if __name__ == "__main__":
    main()
