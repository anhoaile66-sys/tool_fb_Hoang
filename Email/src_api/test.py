import requests

# Base URL for the API endpoint
BASE_URL = 'http://localhost:5468'

# List of example emp_ids and their corresponding template data
# We need 11 distinct emp_ids as requested by the user.
# Using a range of emp_ids for testing purposes.
templates_to_add = [
    {"emp_id": '22615833', "subject": "Cơ hội việc làm IT hấp dẫn 1", "content": "Nội dung email 1: Chúng tôi có nhiều vị trí IT đang tuyển dụng."},
    {"emp_id": '22636101', "subject": "Tuyển dụng Chuyên viên Marketing 2", "content": "Nội dung email 2: Tìm kiếm tài năng Marketing cho đội ngũ của chúng tôi."},
    {"emp_id": '22789191', "subject": "Kỹ sư phần mềm cấp cao 3", "content": "Nội dung email 3: Tham gia đội ngũ phát triển sản phẩm hàng đầu."},
    {"emp_id": '22814414', "subject": "Thực tập sinh Data Analyst 4", "content": "Nội dung email 4: Cơ hội học hỏi và phát triển trong lĩnh vực phân tích dữ liệu."},
    {"emp_id": '22833463', "subject": "Chuyên viên tư vấn tài chính 5", "content": "Nội dung email 5: Xây dựng sự nghiệp vững chắc với chúng tôi."},
    {"emp_id": '22889226', "subject": "Quản lý dự án IT 6", "content": "Nội dung email 6: Dẫn dắt các dự án công nghệ đột phá."},
    {"emp_id": '22894754', "subject": "Thiết kế đồ họa sáng tạo 7", "content": "Nội dung email 7: Biến ý tưởng thành hiện thực với thiết kế ấn tượng."},
    {"emp_id": '22889521', "subject": "Nhân viên kinh doanh B2B 8", "content": "Nội dung email 8: Phát triển mạng lưới khách hàng doanh nghiệp."},
    {"emp_id": '22614471', "subject": "Chuyên viên hỗ trợ kỹ thuật 9", "content": "Nội dung email 9: Giải quyết các vấn đề kỹ thuật cho khách hàng."},
    {"emp_id": '22896992', "subject": "Kế toán tổng hợp 10", "content": "Nội dung email 10: Đảm bảo hoạt động tài chính minh bạch."},
    {"emp_id": '22616467', "subject": "Trưởng phòng nhân sự 11", "content": "Nội dung email 11: Xây dựng và phát triển đội ngũ nhân tài."},
    {"emp_id": '22846622', 'subject': "Chuyên viên SEO 12", "content": "Nội dung email 12: Tối ưu hóa công cụ tìm kiếm để tăng cường hiện diện trực tuyến."}
]

for template_data in templates_to_add:
    response = requests.post(f'{BASE_URL}/set-template', json=template_data)
    print(f"Response for emp_id {template_data['emp_id']}: {response.json()}")
