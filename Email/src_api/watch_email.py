import time
import os
import sqlite3
from datetime import datetime
from classSend import run_sent
from classHtmlRender import run_simulator

# --- Cấu hình biến truyền vào api ---
# EMP_ID is now dynamically read from the database
SUBJECT = ""
CONTENT = ""

MODE = 2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSINESS_SUBJECT_PATH = os.path.join(BASE_DIR, "..", "business", "business_subject_sample.txt")
BUSINESS_WRITEN_MAIL_PATH = os.path.join(BASE_DIR, "..", "business", "business_writen_mail_sample.txt")
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

def get_pending_customers(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_id, customer_email, subject, content FROM customers WHERE emp_id = ? AND sent = 0",
        "UPDATE customers SET sent = ? WHERE customer_id = ?",
        (sent_status, customer_id)
    )
    conn.commit()
    conn.close()

def get_email_account_for_sending(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT email_account, id FROM email_accounts WHERE emp_id = ? AND is_active = 1 ORDER BY num_sent ASC LIMIT 1",
        (emp_id,)
    )
    account = cursor.fetchone()
    conn.close()
    return account

def update_email_account_sent_count(account_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE email_accounts SET num_sent = num_sent + 1 WHERE id = ?",
        (account_id,)
    )
    conn.commit()
    conn.close()

def process_pending_emails(emp_id):
    global SUBJECT, CONTENT
    print(f"👂 Đang kiểm tra khách hàng mới cho EMP_ID: {emp_id}...")
    
    pending_customers = get_pending_customers(emp_id)

    if pending_customers:
        print(f"🔔 Có {len(pending_customers)} khách hàng mới, chạy gửi lấy html và gửi mail...")
        for customer in pending_customers:
            customer_id = customer["customer_id"]
            customer_email = customer["customer_email"]
            mail_subject = customer["subject"] if customer["subject"] else SUBJECT
            mail_content = customer["content"] if customer["content"] else CONTENT

            email_account = get_email_account_for_sending(emp_id)
            if not email_account:
                print(f"⚠️ Không tìm thấy tài khoản email hoạt động để gửi cho EMP_ID: {emp_id}")
                break # Stop processing for this emp_id if no active email account

            sender_email = email_account["email_account"]
            email_account_id = email_account["id"]

            print(f"✉️ Đang gửi email cho {customer_email} từ {sender_email}...")
            
            simulator = run_simulator(emp_id, BUSINESS_SUBJECT_PATH, BUSINESS_WRITEN_MAIL_PATH, MODE=MODE)
            simulator.set_subject(mail_subject)
            simulator.set_content(mail_content)
            simulator.beautify_html()
            
            final_subject = simulator.get_subject()
            final_content = simulator.get_content()

            # Assuming run_sent handles the actual sending and returns success/failure
            # For now, we'll assume it always succeeds for the purpose of this refactor
            success = run_sent(emp_id, final_subject, final_content, customer_email, sender_email) 
            
            if success:
                update_customer_sent_status(customer_id, 1)
                update_email_account_sent_count(email_account_id)
                print(f"✅ Đã gửi email thành công cho {customer_email}.")
            else:
                print(f"❌ Gửi email thất bại cho {customer_email}.")
                # Optionally, handle retry logic or mark as failed in DB
    else:
        print("ℹ️ Chưa có khách hàng mới, đợi update tiếp.")

while True:
    process_pending_emails(EMP_ID)
    time.sleep(300)  # check lại sau 300 giây