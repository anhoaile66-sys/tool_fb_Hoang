from datetime import datetime
from pydoc import doc
from bson import ObjectId
import motor.motor_asyncio
import logging
import pymongo
import urllib
import json
#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh chung
def get_client_name(Type="Base"):
    with open("DatabaseAccounts.env", "r") as file:
        data = json.load(file).get(Type, {})
    username = urllib.parse.quote_plus(data["username"])
    password = urllib.parse.quote_plus(data["pwd"])
    return f"mongodb://{username}:{password}@123.24.206.25:27017/?authSource=admin"

def get_async_collection(collection_name, client_name=get_client_name(), db_name="Facebook"):
    """Tạo async collection client"""
    client = motor.motor_asyncio.AsyncIOMotorClient(client_name)
    db = client[db_name]
    collection = db[collection_name]
    return collection

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan đến collection "Link-groups"
async def get_groups_links():
    """Lấy danh sách các liên kết nhóm từ cơ sở dữ liệu."""
    collection = get_async_collection("Link-groups")
    return await collection.find().to_list(length=None)

async def get_group_to_join(FB_id):
    """Lấy liên kết nhóm từ cơ sở dữ liệu để tham gia."""
    collection = get_async_collection("Link-groups")
    cursor = collection.aggregate([
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
            "$limit": 1
        }
    ])
    
    groups = await cursor.to_list(length=1)
    if groups:
        group = groups[0]
        await collection.update_one(
            {"_id": group["_id"]}, 
            {"$addToSet": {"Temp_Joined_Accounts": FB_id}}
        )
        return group['Link']
    return None

async def update_group_name(group_link, new_name):
    """Cập nhật tên nhóm trong cơ sở dữ liệu."""
    collection = get_async_collection("Link-groups")
    result = await collection.update_one(
        {"Link": group_link}, 
        {"$set": {"Name": new_name}}
    )
    if result.matched_count == 0:  
        return {'message': '❌ Nhóm không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Tên nhóm không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật thành công'}, logging.INFO

async def update_group_status(group_link, status, number_of_posts):
    """Cập nhật trạng thái nhóm trong cơ sở dữ liệu."""
    collection = get_async_collection("Link-groups")
    result = await collection.update_one(
        {"Link": group_link}, 
        {"$set": {"Status": status, "Number_Of_Posts": number_of_posts}}
    )
    if result.matched_count == 0:
        return {'message': '❌ Nhóm không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Trạng thái nhóm không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật thành công'}, logging.INFO

async def update_temp_joined_accounts(user_id, group_link):
    """Thêm user_name vào danh sách các tài khoản tạm thời tham gia nhóm"""
    collection = get_async_collection("Link-groups")
    result = await collection.update_one(
        {"Link": group_link},
        {"$addToSet": {"Temp_Joined_Accounts": user_id}}
    )
    if result.matched_count == 0:
        return {'message': f'❌ Cập nhật tài khoản gửi yêu cầu tham gia nhóm: Nhóm {group_link} không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': f'⚠️ Cập nhật tài khoản gửi yêu cầu tham gia nhóm: Nhóm {group_link} không có thay đổi nào'}, logging.WARNING
    return {'message': f'✅ Cập nhật tài khoản gửi yêu cầu tham gia nhóm: Nhóm {group_link} đã gửi yêu cầu tham gia thành công'}, logging.INFO

async def update_joined_accounts(user_id, group_link):
    """Thêm user_name vào danh sách các tài khoản đã tham gia nhóm"""
    collection = get_async_collection("Link-groups")
    result = await collection.update_one(
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

async def get_unapproved_groups(user_id):
    """Lấy danh sách các nhóm chưa được phê duyệt."""
    collection = get_async_collection("Link-groups")
    groups = await collection.find({"Temp_Joined_Accounts": user_id}).to_list(length=None)
    return groups
#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "Binh-luan"
async def save_comment(group_name, post_link, content, comment, post_type, post_keywords):
    """Lưu bình luận vào cơ sở dữ liệu."""
    collection = get_async_collection("Binh-luan")
    await collection.insert_one({
        "Group_name": group_name,
        "Link-post": post_link,
        "Content": content,
        "Comment": comment,
        "Type": post_type,
        "Keywords": post_keywords,
        "Status": "Chưa xử lý",
        "Time": datetime.now()
    })

async def get_comment(user_id):
    """Lấy bình luận để xử lý"""
    # Kiểm tra KPI
    if not await check_kpi(user_id, "Bình luận"): 
        return {'message': '⚠️ Bình luận thương hiệu: Đã đạt KPI, không thể lấy bình luận'}, logging.WARNING

    # Tìm bình luận chưa xử lý mới nhất
    binh_luan_collection = get_async_collection("Binh-luan")
    binh_luan_moi_nhat = await binh_luan_collection.find_one(
        {"Status": "Chưa xử lý"},
        sort=[("Time", -1)]
    )

    if not binh_luan_moi_nhat:
        return {'message': '⚠️ Bình luận thương hiệu: Không có bình luận nào chưa xử lý'}, logging.WARNING

    # Lấy dữ liệu từ bản ghi mới nhất
    group_name = binh_luan_moi_nhat.get("Group_name")
    post_link = binh_luan_moi_nhat.get("Link-post")
    Content = binh_luan_moi_nhat.get("Content")
    Comment = binh_luan_moi_nhat.get("Comment")

    # Thêm bản ghi vào bảng thống kê
    print(Content)
    thong_ke_collection = get_async_collection("Thong-ke-binh-luan")
    await thong_ke_collection.insert_one({
        "Group_name": group_name,
        "Link-post": post_link,
        "Content": Content,
        "Comment": Comment,
        "Time": datetime.now().timestamp(),
        "Commented_by": user_id
    })

    # Gọi hàm cập nhật trạng thái bài viết
    await update_crawled_post_status(post_link, "Đã bình luận")

    # Cập nhật trạng thái bình luận
    await binh_luan_collection.update_one(
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
async def get_account(user_id):
    collection = get_async_collection("Users")
    user = await collection.find_one({"user_id": user_id})
    if not user:
        comment_count = await get_async_collection("Thong-ke-binh-luan").count_documents({"Commented_by": user_id})
        group_count = await get_async_collection("Link-groups").count_documents(
            {
                "$or": [
                    {"Joined_Accounts": user_id},
                    {"Temp_Joined_Accounts": user_id}
                ]
            }
        )
        result = await collection.insert_one({"user_id": user_id, "kpi": {"Bình luận": comment_count + 1, "Tham gia nhóm": group_count + 5}, "kpi_per_day": {"Bình luận": 1, "Tham gia nhóm": 5}})
        if result.inserted_id:
            user = await collection.find_one({"_id": result.inserted_id})
    return user

async def check_kpi(user_id, kpi_type):
    """Kiểm tra KPI của người dùng."""
    user = await get_account(user_id)
    if not user:
        return False
    kpi = user.get("kpi", {}).get(kpi_type, 0)
    
    if kpi_type == "Bình luận":
        done = await get_async_collection("Thong-ke-binh-luan").count_documents({"Commented_by": user_id})
        return done < kpi
    if kpi_type == "Tham gia nhóm":
        done = await get_async_collection("Link-groups").count_documents({"Joined_Accounts": user_id})
        return done < kpi
    return False

async def update_daily_kpi():
    users_collection = get_async_collection("Users")
    comments_collection = get_async_collection("Thong-ke-binh-luan")
    groups_collection = get_async_collection("Link-groups")

    users = await users_collection.find({}, {"_id": 1, "user_id": 1, "kpi_per_day": 1}).to_list(length=None)
    updates = []

    for user in users:
        user_id = user.get("user_id")
        kpi_per_day = user.get("kpi_per_day", {})
        if not user_id:
            continue

        # Đếm số bình luận
        comment_count = await comments_collection.count_documents({ "Comment_by": user_id })

        # Đếm số nhóm đã tham gia
        group_join_count = await groups_collection.count_documents({
            "$or": [
                { "Joined_Accounts": user_id },
                { "Temp_Joined_Accounts": user_id }
            ]
        })

        # Tạo kpi mới
        new_kpi = {
            "Bình luận": comment_count + kpi_per_day.get("Bình luận", 0),
            "Tham gia nhóm": group_join_count + kpi_per_day.get("Tham gia nhóm", 0)
        }

        updates.append(pymongo.UpdateOne(
            { "_id": user["_id"] },
            { "$set": { "kpi": new_kpi } }
        ))

    if updates:
        await users_collection.bulk_write(updates)
#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "Questions"
async def upload_question(group_link, question, how_to_answer, answers):
    """Tải lên câu hỏi vào cơ sở dữ liệu."""
    collection = get_async_collection("Questions")
    # Kiểm tra câu hỏi đã tồn tại chưa
    existing_question = await collection.find_one({
        "Group_link": group_link,
        "Question": question,
    })
    if existing_question:
        return {'message': '⚠️ Tải lên câu hỏi: Câu hỏi đã tồn tại'}, logging.WARNING
    
    await collection.insert_one({
        "Group_link": group_link,
        "Question": question,
        "How_to_answer": how_to_answer,
        "Answers": answers,
        "Time": datetime.now(),
        "Status": "Chưa xử lý",
        "Answer": None
    })
    return {'message': '✅ Tải lên câu hỏi: Thành công'}, logging.INFO

async def get_answer(group_link, question):
    """Lấy câu trả lời cho câu hỏi từ cơ sở dữ liệu."""
    collection = get_async_collection("Questions")
    existing_question = await collection.find_one({
        "Group_link": group_link,
        "Question": question
    })
    if existing_question:
        if existing_question["Status"] == "Đã trả lời":
            return {'message': f'✅ Lấy câu trả lời: Câu hỏi "{question}": Thành công', 'answer': existing_question["Answer"]}, logging.INFO
    return {'message': f'⚠️ Lấy câu trả lời: Câu hỏi "{question}": Chưa được trả lời'}, logging.WARNING

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection Commands
async def get_commands(user_id, status="Chưa xử lý"):
    """Lấy thông tin lệnh từ cơ sở dữ liệu."""
    collection = get_async_collection("Commands")
    commands = await collection.find({"user_id": user_id, "Status": status}).to_list(length=None)
    if status == "Chưa xử lý":
        collection.update_many(
            {"user_id": user_id, "Status": status},
            {"$set": {"Status": "Đang thực hiện"}}
        )
    return commands

async def execute_command(command_id, status):
    """Thực hiện lệnh cho người dùng."""
    collection = get_async_collection("Commands")
    result = await collection.update_one(
        {"_id": ObjectId(command_id)},
        {"$set": {"Status": status, "Executed_at": datetime.now()}}
    )
    if result.matched_count == 0:
        return {"message": "❌ Cập nhật trạng thái lệnh: Lệnh không tồn tại"}, logging.ERROR
    if result.modified_count == 0:
        return {"message": "⚠️ Cập nhật trạng thái lệnh: Lệnh không có thay đổi nào"}, logging.WARNING
    
    # Lấy thông tin lệnh đã thực hiện
    command = await collection.find_one({"_id": ObjectId(command_id)})
    type = command.get("type")
    if type == "post_to_group":
        params = command.get("params") if command else None
        bai_dang_collection = get_async_collection("Bai-dang")
        await bai_dang_collection.update_one(
            {"_id": ObjectId(params["oid"])},
            {"$set": {"status": "Đang chờ duyệt"}}
        )
    if type == "post_to_wall":
        params = command.get("params") if command else None
        bai_dang_tuong_collection = get_async_collection("Bai-dang-tuong")
        await bai_dang_tuong_collection.update_one(
            {"_id": ObjectId(params["oid"])},
            {"$set": {"status": "Đang đăng"}}
        )
    return {"message": "✅ Cập nhật trạng thái lệnh: Lệnh đã được thực hiện"}, logging.INFO

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection Bai-dang và Bai-dang-tuong
async def get_unapproved_posts(user_id):
    """Lấy danh sách bài viết chưa được phê duyệt của người dùng."""
    collection = get_async_collection("Bai-dang")
    posts = await collection.find({"user_id": user_id, "status": "Đang chờ duyệt"}).to_list(length=None)
    return posts

async def get_unapproved_wall_posts(user_id):
    """Lấy danh sách bài viết chưa được phê duyệt trên tường của người dùng."""
    collection = get_async_collection("Bai-dang-tuong")
    posts = await collection.find({"user_id": user_id, "status": "Đang đăng"}).to_list(length=None)
    return posts

async def update_post_status(post_id, status, link):
    """Cập nhật trạng thái bài viết."""
    collection = get_async_collection("Bai-dang")
    result = await collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"status": status, "updated_at": datetime.now(), "link": link}}
    )
    if result.matched_count == 0:
        return {"message": "❌ Cập nhật trạng thái bài viết: Bài viết không tồn tại"}, logging.ERROR
    if result.modified_count == 0:
        return {"message": "⚠️ Cập nhật trạng thái bài viết: Trạng thái bài viết không thay đổi"}, logging.WARNING
    return {"message": "✅ Cập nhật trạng thái bài viết: Thành công, link: " + link}, logging.INFO

async def update_wall_post_status(post_id, status, link):
    """Cập nhật trạng thái bài viết trên tường."""
    collection = get_async_collection("Bai-dang-tuong")
    result = await collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"status": status, "updated_at": datetime.now(), "link": link}}
    )
    if result.matched_count == 0:
        return {"message": "❌ Cập nhật trạng thái bài viết trên tường: Bài viết không tồn tại"}, logging.ERROR
    if result.modified_count == 0:
        return {"message": "⚠️ Cập nhật trạng thái bài viết trên tường: Trạng thái bài viết không thay đổi"}, logging.WARNING
    return {"message": "✅ Cập nhật trạng thái bài viết trên tường: Thành công, link: " + link}, logging.INFO
#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "Danh-sach-bai-dang"
async def update_crawled_post_status(post_link, status):
    """Cập nhật trạng thái bài viết trong cơ sở dữ liệu."""
    collection = get_async_collection("Danh-sach-bai-dang")
    result = await collection.update_one(
        {"Link-post": post_link}, 
        {"$set": {"Status": status}}
    )
    if result.matched_count == 0:
        return {'message': '❌ Bài viết không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Trạng thái bài viết không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật thành công'}, logging.INFO
#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection Binh-luan-trong-bai-dang
async def save_post_comment(post_link, commenter, comment, time, level=0, parent_commenter=None, parent_comment=None):
    """Lưu bình luận trong bài đăng vào cơ sở dữ liệu."""
    collection = get_async_collection("Binh-luan-trong-bai-dang")
    parent_id = None
    
    if level > 0:
        if not parent_commenter or not parent_comment:
            return {'message': '❌ Lưu bình luận trong bài đăng: Thiếu thông tin bình luận cha'}, logging.ERROR
        # Lấy id của bình luận cha
        parent = await collection.find_one({
            "Post_link": post_link,
            "Commenter": parent_commenter,
            "Comment": parent_comment,
            "Level": level - 1
        })
        if not parent:
            return {'message': '❌ Lưu bình luận trong bài đăng: Không tìm thấy bình luận cha'}, logging.ERROR
        parent_id = parent.get("_id")
    
    # Lưu bình luận mới
    result = await collection.insert_one({
        "Post_link": post_link,
        "Commenter": commenter,
        "Comment": comment,
        "Time": time,
        "Level": level,
        "Parent_id": parent_id
    })
    
    if result.inserted_id:
        return {'message': '✅ Lưu bình luận trong bài đăng: Thành công'}, logging.INFO
    return {'message': '❌ Lưu bình luận trong bài đăng: Thất bại'}, logging.ERROR

#-------------------------------------------------------------------------------------------------------------------------------
# Lệnh liên quan tới collection "devices"
async def get_account_by_username(username):
    """Lấy tài khoản theo username."""
    collection = get_async_collection("devices")
    device = await collection.find_one({"accounts.account": username})
    if not device:
        return None
    account = next(
        (acc for acc in device["accounts"] if acc["account"] == username),
            None
        )
    if not account:
        device_id = None
    else:
        device_id = device.get("device_id")
    return account, device_id

async def update_statusFB(username, statusFB):
    """Cập nhật trạng thái Facebook của thiết bị."""
    collection = get_async_collection("devices")
    if statusFB == "Online":
        result = await collection.update_one(
            {"accounts.account": username},
            {"$set": {
                "current_account": username,
                "time_logged_in": datetime.now(),
                "accounts.$[elem].status": statusFB
                }
            },
            array_filters=[{"elem.account": username}]
        )
    elif statusFB == "Offline":
        result = await collection.update_many(
            {"device_id": username},
            {"$set": {
                "accounts.$[elem].status": "Offline",
                "time_logged_in": None,
                "current_account": ""
                }
            },
            array_filters=[{"elem.status": "Online"}]
        )
    elif statusFB == "Crash":
        result = await collection.update_one(
            {"accounts.account": username},
            {"$set": {
                "accounts.$[elem].status": statusFB,
                "time_logged_in": None,
                "current_account": ""}
            },
            array_filters=[{"elem.account": username}]
        )
    if result.matched_count == 0:
        return {'message': '❌ Thiết bị không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Trạng thái Facebook không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật trạng thái Facebook thành công'}, logging.INFO

async def update_device_status(device_id, status):
    """Cập nhật trạng thái hoạt động của thiết bị."""
    collection = get_async_collection("devices")
    if device_id is None:
        result = await collection.update_many(
            {},
            {"$set": {"status": status}}
        )
    else:   
        result = await collection.update_one(
            {"device_id": device_id},
            {"$set": {"status": status}}
        )
    if result.matched_count == 0:
        return {'message': '❌ Thiết bị không tồn tại'}, logging.ERROR
    if result.modified_count == 0:
        return {'message': '⚠️ Trạng thái thiết bị không thay đổi'}, logging.WARNING
    return {'message': '✅ Cập nhật trạng thái thiết bị thành công'}, logging.INFO