import sys
import os
from flask import Flask, request, jsonify
from datetime import datetime

# Add the project root directory to sys.path to enable relative imports when running directly
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Email.business.create_business_db import add_customer_safe

app = Flask(__name__)

@app.route('/add-email', methods=['POST'])
def add_email():
    data = request.get_json(silent=True)
    if data and "email" in data:
        email = data["email"]
    elif "email" in request.form:
        email = request.form["email"]
    else:
        return jsonify({"error": "Thiếu biến 'email'"}), 400
        
    if data and "emp_id" in data:
        emp_id = data["emp_id"]
    elif "emp_id" in request.form:
        emp_id = request.form["emp_id"]
    else:
        return jsonify({"error": "Thiếu biến 'emp_id'"}), 400
    
    if data and "subject" in data:
        subject = data["subject"]
    elif "subject" in request.form:
        subject = request.form["subject"]
    else:
        return jsonify({"error": "Thiếu biến 'subject'"}), 400
    
    if data and "content" in data:
        content = data["content"]
    elif "content" in request.form:
        content = request.form["content"]
    else:
        return jsonify({"error": "Thiếu biến 'content'"}), 400

    # Use add_customer_safe to add the email to the database
    success = add_customer_safe(emp_id=emp_id, customer_email=email, sent=0, subject=subject, content=content)
    
    if success:
        print(f"✅ Thêm email {email} cho emp_id {emp_id} vào DB")
        return jsonify({
            "status": "added", 
            "emp_id": emp_id, 
            "email": email,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
    else:
        print(f"ℹ️ Email {email} đã tồn tại cho emp_id {emp_id} trong ngày hôm nay hoặc có lỗi xảy ra")
        return jsonify({
            "status": "existed_today_or_error", 
            "message": f"Email {email} đã được thêm cho emp_id {emp_id} trong ngày hôm nay hoặc có lỗi xảy ra",
            "emp_id": emp_id, 
            "email": email,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5468, debug=True)
