from datetime import datetime
from bson import ObjectId
import pymongo
import logging

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh chung
def get_collection(collection_name, client_name = "mongodb://localhost:27017/", db_name = "Facebook"):
    client = pymongo.MongoClient(client_name)
    db = client[db_name]
    collection = db[collection_name]
    return collection

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan đến collection "Link-groups"
def get_groups_links():
    """Lấy danh sách các liên kết nhóm từ cơ sở dữ liệu."""
    collection = get_collection("Link-groups")
    return list(collection.find())

def get_group_to_join(FB_id):
    """Lấy liên kết nhóm từ cơ sở dữ liệu."""
    collection = get_collection("Link-groups")
    group = collection.aggregate([
        {
            "$match": {
                "Status": "Hoạt động",
                "Joined_Accounts": {
                    "$not": { "$elemMatch": { "$eq": FB_id } }
                },
                "Temp_Joined_Accounts": {
                    "$not": { "$elemMatch": { "$eq": FB_id } }
                }
            }
        },
        {
            "$addFields": {
                "Joined_Count": { 
                    "$add": [
                        { "$size": { "$ifNull": ["$Joined_Accounts", []] } },
                        { "$size": { "$ifNull": ["$Temp_Joined_Accounts", []] } }
                    ]
                }
            }
        },
        {
            "$sort": { 
                "Joined_Count": 1,
                "Number_Of_Posts": -1
            }  
        },
        {
            "$limit": 1  # Chỉ lấy 1 bản ghi đầu tiên
        }
    ])
    group = next(group, None)
    if group:
        get_collection("Link-groups").update_one({"_id": group["_id"]}, {"$addToSet": {"Temp_Joined_Accounts": FB_id}})
        return group['Link']
    return None

def update_group_name(group_link, new_name):
    """Cập nhật tên nhóm trong cơ sở dữ liệu."""
    collection = get_collection("Link-groups")
    result = collection.update_one({"Link": group_link}, {"$set": {"Name": new_name}})
    if result.matched_count == 0:  
        return {'message': '❌ Nhóm không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Tên nhóm không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật thành công'}, logging.INFO

def update_group_status(group_link, status, number_of_posts):
    """Cập nhật trạng thái nhóm trong cơ sở dữ liệu."""
    collection = get_collection("Link-groups")
    result = collection.update_one({"Link": group_link}, {"$set": {"Status": status, "Number_Of_Posts": number_of_posts}})
    if result.matched_count == 0:
        return {'message': '❌ Nhóm không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Trạng thái nhóm không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật thành công'}, logging.INFO

def update_temp_joined_accounts(user_id, group_link):
    # Thêm user_name vào danh sách các tài khoản tạm thời tham gia nhóm
    collection = get_collection("Link-groups")
    result = collection.update_one(
        {"Link": group_link},
        {"$addToSet": {"Temp_Joined_Accounts": user_id}}
    )
    if result.matched_count == 0:
        return {'message': f'❌ Cập nhật tài khoản gửi yêu cầu tham gia nhóm: Nhóm {group_link} không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': f'⚠️ Cập nhật tài khoản gửi yêu cầu tham gia nhóm: Nhóm {group_link} không có thay đổi nào'}, logging.WARNING
    return {'message': f'✅ Cập nhật tài khoản gửi yêu cầu tham gia nhóm: Nhóm {group_link} đã gửi yêu cầu tham gia thành công'}, logging.INFO

def update_joined_accounts(user_id, group_link):
    # Thêm user_name vào danh sách các tài khoản đã tham gia nhóm
    collection = get_collection("Link-groups")
    result = collection.update_one(
        {"Link": group_link},
        {
            "$addToSet": {"Joined_Accounts": user_id},
            "$pull": {"Temp_Joined_Accounts": user_id}
        }
    )
    
    if result.matched_count == 0:
        return {'message': f'❌ Cập nhật tài khoản đã tham gia nhóm: Nhóm {group_link} không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': f'⚠️ Cập nhật tài khoản đã tham gia nhóm: Nhóm {group_link} không có thay đổi nào'}, logging.WARNING
    return {'message': f'✅ Cập nhật tài khoản đã tham gia nhóm: Nhóm {group_link} đã tham gia thành công'}, logging.INFO

def get_unapproved_groups(user_id):
    """Lấy danh sách các nhóm chưa được phê duyệt."""
    collection = get_collection("Link-groups")
    groups = collection.find({"Temp_Joined_Accounts": user_id})
    return list(groups)

# Chuyển thành server socket
def get_groups_data(user_id, group_name = None, limit=0, page=1):
    """Lấy dữ liệu nhóm từ cơ sở dữ liệu."""
    collection = get_collection("Link-groups")
    
    # Tạo pipeline aggregation
    pipeline = []
    
    # Bước 1: Match theo điều kiện cơ bản
    match_stage = {}
    if group_name:
        match_stage["Name"] = {"$regex": group_name, "$options": "i"}
    
    if user_id:
        match_stage["$or"] = [
            {"Joined_Accounts": {"$in": [user_id]}},
            {"Temp_Joined_Accounts": {"$in": [user_id]}}
        ]
    
    if match_stage:
        pipeline.append({"$match": match_stage})
    
    # Bước 2: Thêm trường trạng thái dựa trên user_id
    if user_id:
        pipeline.append({
            "$addFields": {
                "user_status": {
                    "$cond": {
                        "if": {"$in": [user_id, {"$ifNull": ["$Joined_Accounts", []]}]},
                        "then": "Đã tham gia",
                        "else": {
                            "$cond": {
                                "if": {"$in": [user_id, {"$ifNull": ["$Temp_Joined_Accounts", []]}]},
                                "then": "Chờ duyệt",
                                "else": "Chưa tham gia"
                            }
                        }
                    }
                }
            }
        })
    else:
        # Nếu không có user_id, set trạng thái mặc định
        pipeline.append({
            "$addFields": {
                "user_status": "Không xác định"
            }
        })
    
    # Bước 3: Sắp xếp
    pipeline.append({"$sort": {"Name": 1}})
    
    # Bước 4: Phân trang
    if limit > 0:
        skip = (page - 1) * limit
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": limit})
    
    return list(collection.aggregate(pipeline))

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "Danh-sach-bai-dang"
def update_crawled_post_status(post_link, status):
    """Cập nhật trạng thái bài viết trong cơ sở dữ liệu."""
    collection = get_collection("Danh-sach-bai-dang")
    result = collection.update_one({"Link-post": post_link}, {"$set": {"Status": status}})
    if result.matched_count == 0:
        return {'message': '❌ Bài viết không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Trạng thái bài viết không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật thành công'}, logging.INFO

def get_post_to_comment():
    """Lấy bài viết cần bình luận từ cơ sở dữ liệu."""
    collection = get_collection("Danh-sach-bai-dang")
    post = collection.find_one({"Status": "Chưa xử lý", "Type": "Ứng viên"})
    if post is None:
        post = collection.find_one({"Status": "Chưa xử lý", "Type": "Nhà tuyển dụng"})
        if post is None:
            return None, None, None
    update_crawled_post_status(post['Link-post'], "Đang xử lý")
    return post['Content'], post['Link-post'], post['Type']

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "Binh-luan"
def save_comment(group_name, post_link, content, comment, post_type, post_keywords):
    """Lưu bình luận vào cơ sở dữ liệu."""
    collection = get_collection("Binh-luan")
    collection.insert_one({
        "Group_name": group_name,
        "Link-post": post_link,
        "Content": content,
        "Comment": comment,
        "Type": post_type,
        "Keywords": post_keywords,
        "Status": "Chưa xử lý",
        "Time": datetime.now()
    })

def get_comment(user_id):
    # Kiểm tra KPI
    if not check_kpi(user_id, "Bình luận"): 
        return {'message': '⚠️ Bình luận thương hiệu: Đã đạt KPI, không thể lấy bình luận'}, logging.WARNING

    # Tìm bình luận chưa xử lý mới nhất
    binh_luan_collection = get_collection("Binh-luan")
    binh_luan_moi_nhat = binh_luan_collection.find_one(
        {"Status": "Chưa xử lý"},
        sort=[("Time", -1)]
    )

    if not binh_luan_moi_nhat:
        return {'message': '⚠️ Bình luận thương hiệu: Không có bình luận nào chưa xử lý'}, logging.WARNING

    # Lấy dữ liệu từ bản ghi mới nhất
    group_name = binh_luan_moi_nhat.get("Group_name")
    post_link = binh_luan_moi_nhat.get("Link-post")
    Content = '\n'.join(binh_luan_moi_nhat.get("Content").split("\n")[1:])
    Comment = binh_luan_moi_nhat.get("Comment")

    # Thêm bản ghi vào bảng thống kê
    thong_ke_collection = get_collection("Thong-ke-binh-luan")
    thong_ke_collection.insert_one({
        "Group_name": group_name,
        "Link-post": post_link,
        "Content": Content,
        "Comment": Comment,
        "Time": datetime.now().timestamp(),
        "Commented_by": user_id
    })

    # Gọi hàm cập nhật trạng thái bài viết
    update_crawled_post_status(post_link, "Đã bình luận")

    # Cập nhật trạng thái bình luận
    binh_luan_collection.update_one(
        {"_id": binh_luan_moi_nhat["_id"]},
        {"$set": {"Status": "Đã bình luận"}}
    )

    return {
        'message': f'✅ Bình luận thương hiệu: Đã bình luận "{Comment}" vào bài viết {post_link}',
        'comment': Comment,
        'link': post_link
    }, logging.INFO

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "Users"
def get_account(user_id):
    collection = get_collection("Users")
    return collection.find_one({"user_id": user_id})

def login(user_id, fb_name):
    collection = get_collection("Users")
    existing_user = collection.find_one({"user_id": user_id})
    if not existing_user:
        collection.insert_one({"user_id": user_id, "kpi": {"Bình luận": 10, "Tham gia nhóm": 10}, "kpi_per_day": {"Bình luận": 10, "Tham gia nhóm": 10}, "fb_name": fb_name})
    else:
        collection.update_one({"user_id": user_id}, {"$set": {"fb_name": fb_name}})

def check_kpi(user_id, kpi_type):
    """Kiểm tra KPI của người dùng."""
    user = get_account(user_id)
    if not user:
        return False
    kpi = user.get("kpi", {}).get(kpi_type, 0)
    if kpi_type == "Bình luận":
        done = get_collection("Thong-ke-binh-luan").count_documents({"Commented_by": user_id})
        return done < kpi
    if kpi_type == "Tham gia nhóm":
        done = get_collection("Link-groups").count_documents({"Joined_Accounts": user_id})
        return done < kpi
    return False

# Chuyển thành server socket
def update_kpi(user_id, kpi_type, kpi_value):
    """Cập nhật KPI cho người dùng."""
    collection = get_collection("Users")
    result = collection.update_one({"user_id": user_id}, {"$set": {f"kpi_per_day.{kpi_type}": kpi_value}})
    if result.matched_count == 0:
        return "Không tìm thấy người dùng", 404
    if result.modified_count == 0:
        return "KPI không thay đổi", 400
    return "Cập nhật KPI thành công", 200

def update_daily_kpi():
    collection = get_collection("Users")
    users = list(collection.find({}, {"kpi": 1, "kpi_per_day": 1}))

    updates = []

    for user in users:
        kpi = user.get("kpi", {})
        kpi_per_day = user.get("kpi_per_day", {})
        new_kpi = {}

        for key in kpi:
            new_kpi[key] = kpi.get(key, 0) + kpi_per_day.get(key, 0)

        updates.append(pymongo.UpdateOne(
            { "_id": user["_id"] },
            { "$set": { "kpi": new_kpi } }
        ))
    if updates:
        collection.bulk_write(updates)

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "Questions"
def upload_question(group_link, question, how_to_answer, answers):
    """Tải lên câu hỏi vào cơ sở dữ liệu."""
    collection = get_collection("Questions")
    # Kiểm tra câu hỏi đã tồn tại chưa
    existing_question = collection.find_one(
        {
            "Group_link": group_link,
            "Question": question,
        }
    )
    if existing_question:
        return {'message': '⚠️ Tải lên câu hỏi: Câu hỏi đã tồn tại'}, logging.WARNING
    collection.insert_one({
        "Group_link": group_link,
        "Question": question,
        "How_to_answer": how_to_answer,
        "Answers": answers,
        "Time": datetime.now(),
        "Status": "Chưa xử lý",
        "Answer": None
    })
    return {'message': '✅ Tải lên câu hỏi: Thành công'}, logging.INFO

def get_answer(group_link, question):
    """Lấy câu trả lời cho câu hỏi từ cơ sở dữ liệu."""
    collection = get_collection("Questions")
    existing_question = collection.find_one(
        {
            "Group_link": group_link,
            "Question": question
        }
    )
    if existing_question:
        if existing_question["Status"] == "Đã trả lời":
            return {'message': f'✅ Lấy câu trả lời: Câu hỏi "{question}": Thành công', 'answer': existing_question["Answer"]}, logging.INFO
    return {'message': f'⚠️ Lấy câu trả lời: Câu hỏi "{question}": Chưa được trả lời'}, logging.WARNING

# Chuyển thành server socket
def upload_answer(group_link, question, answer):
    """Lưu câu trả lời vào cơ sở dữ liệu."""
    collection = get_collection("Questions")
    result = collection.update_one(
        {
            "Group_link": group_link,
            "Question": question,
        },
        {
            "$set": {"Answer": answer, "Status": "Đã trả lời"}
        }
    )
    if result.matched_count == 0:
        return "Không tìm thấy câu hỏi", 404
    if result.modified_count == 0:
        return "Câu hỏi đã được trả lời trước đó", 400
    return "Cập nhật câu hỏi thành công", 200

# Chuyển thành server socket
def get_question_data(status='', group_name='', limit=0, page=1):
    """Lấy dữ liệu câu hỏi từ cơ sở dữ liệu."""
    # Tạo pipeline truy vấn
    pipeline = []

    # Bước 1: Join với bảng Link-groups
    pipeline.append({
        "$lookup": {
            "from": "Link-groups",
            "localField": "Group_link",  # Trường trong Questions
            "foreignField": "Link",      # Trường trong Link-groups
            "as": "group_info"
        }
    })

    # Bước 2: Tách group_info thành object thay vì array
    pipeline.append({"$unwind": {"path": "$group_info", "preserveNullAndEmptyArrays": True}})

    # Bước 3: Lọc theo status và tên nhóm nếu có
    match_stage = {}
    if status != '':
        match_stage["Status"] = status

    if group_name:
        match_stage["group_info.Name"] = {"$regex": group_name, "$options": "i"}

    if match_stage:
        pipeline.append({"$match": match_stage})

    # Bước 4: Sắp xếp theo thời gian
    pipeline.append({"$sort": {"Time": -1}})

    # Bước 5: Phân trang nếu có
    if limit > 0:
        start = (page - 1) * limit
        pipeline.append({"$skip": start})
        pipeline.append({"$limit": limit})

    # Truy vấn MongoDB
    collection = get_collection("Questions")
    return list(collection.aggregate(pipeline))

#--------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection Commands
# Chuyển thành server socket
def send_command(crm_id, user_id, type, params):
    """Gửi lệnh đến hệ thống."""
    collection = get_collection("Commands")
    if type == "join_group":
        collection.insert_one({
            "crm_id": crm_id,
            "user_id": user_id,
            "type": "join_group",
            "params": params,
            "Status": "Chưa xử lý"
        })
        return "Thêm lệnh thành công", 200
    # if type == "leave_group":
    #     if "group_link" not in params:
    #         return "Thiếu thông tin group_link", 400
    #     collection.insert_one({
    #         "crm_id": crm_id,
    #         "user_id": user_id,
    #         "type": "leave_group",
    #         "params": params,
    #         "Status": "Chưa xử lý"
    #     })
    #     return "Thêm lệnh thành công", 200
    if type == "post_to_group":
        if "group_link" not in params:
            return "Thiếu thông tin group_link", 400
        if "content" not in params:
            return "Thiếu thông tin content", 400
        # Lưu vào collection Bai-dang
        bai_dang_collection = get_collection("Bai-dang")
        result = bai_dang_collection.insert_one({
            "crm_id": crm_id,
            "user_id": user_id,
            "group_link": params["group_link"],
            "content": params["content"],
            "files": params.get("files", []),
            "status": "Chưa xử lý"
        })
        inserted_id = result.inserted_id
        params['oid'] = str(inserted_id)

        collection.insert_one({
            "crm_id": crm_id,
            "user_id": user_id,
            "type": "post_to_group",
            "params": params,
            "Status": "Chưa xử lý",
        })
        
        return "Thêm lệnh thành công", 200
    return "Lệnh không hợp lệ", 400

def get_commands(user_id, status="Chưa xử lý"):
    """Lấy thông tin lệnh từ cơ sở dữ liệu."""
    collection = get_collection("Commands")
    commands = list(collection.find({"user_id": user_id, "Status": status}))
    return commands

def execute_command(command_id):
    """Thực hiện lệnh cho người dùng."""
    collection = get_collection("Commands")
    result = collection.update_one(
        {"_id": ObjectId(command_id)},
        {"$set": {"Status": "Đã thực hiện"}}
    )
    if result.matched_count == 0:
        return {"message": "❌ Cập nhật trạng thái lệnh: Lệnh không tồn tại"}, logging.ERROR
    if result.modified_count == 0:
        return {"message": "⚠️ Cập nhật trạng thái lệnh: Lệnh không có thay đổi nào"}, logging.WARNING
    # Lấy thông tin lệnh đã thực hiện
    command = collection.find_one({"_id": ObjectId(command_id)})
    type = command.get("type")
    if type == "post_to_group":
        params = command.get("params") if command else None
        bai_dang_collection = get_collection("Bai-dang")
        bai_dang_collection.update_one(
            {"_id": ObjectId(params["oid"])},
            {"$set": {"status": "Đang chờ duyệt"}}
        )
    return {"message": "✅ Cập nhật trạng thái lệnh: Lệnh đã được thực hiện"}, logging.INFO

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection Bai-dang
def get_unapproved_posts(user_id):
    """Lấy danh sách bài viết chưa được phê duyệt của người dùng."""
    collection = get_collection("Bai-dang")
    posts = list(collection.find({"user_id": user_id, "status": "Đang chờ duyệt"}))
    return posts

def update_post_status(post_id, status, link):
    """Cập nhật trạng thái bài viết."""
    collection = get_collection("Bai-dang")
    result = collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"status": status, "updated_at": datetime.now(), "link": link}}
    )
    if result.matched_count == 0:
        return {"message": "❌ Cập nhật trạng thái bài viết: Bài viết không tồn tại"}, logging.ERROR
    if result.modified_count == 0:
        return {"message": "⚠️ Cập nhật trạng thái bài viết: Trạng thái bài viết không thay đổi"}, logging.WARNING
    return {"message": "✅ Cập nhật trạng thái bài viết: Thành công, link: " + link}, logging.INFO

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection Binh-luan-trong-bai-dang
def save_post_comment(post_link, commenter, comment, time, level=0, parent_commenter=None, parent_comment=None):
    """Lưu bình luận trong bài đăng vào cơ sở dữ liệu."""
    collection = get_collection("Binh-luan-trong-bai-dang")
    if level > 0:
        if not parent_commenter or not parent_comment:
            return {'message': '❌ Lưu bình luận trong bài đăng: Thiếu thông tin bình luận cha'}, logging.ERROR
        # Lấy id của bình luận cha
        parent = collection.find_one({
            "Post_link": post_link,
            "Commenter": parent_commenter,
            "Comment": parent_comment,
            "Level": level - 1
        })
        if not parent:
            return {'message': '❌ Lưu bình luận trong bài đăng: Không tìm thấy bình luận cha'}, logging.ERROR
        parent_id = parent.get("_id")
    # Lưu bình luận mới
    result = collection.insert_one({
        "Post_link": post_link,
        "Commenter": commenter,
        "Comment": comment,
        "Time": time,
        "Level": level,
        "Parent_id": parent_id if level > 0 else None
    })
    if result.inserted_id:
        return {'message': '✅ Lưu bình luận trong bài đăng: Thành công'}, logging.INFO
    return {'message': '❌ Lưu bình luận trong bài đăng: Thất bại'}, logging.ERROR