import json
import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# socketcorio = SocketIO(app, c)
# cors_allowed_origins='*'
# Chỗ này xem lại xem sử dụng Web Socket được không
socketio = SocketIO(app, async_mode='eventlet',
                    max_http_buffer_size=1024 * 1024 * 1024, cors_allowed_origins='*')

id_port = {
    "22773024": [{"8002": "7DXCUKKB6DVWDAQO"}, {"8006": "CEIN4X45I7ZHFEFU"}, {"8005": "UWJJOJLB85SO7LIZ"}, {"8003": "TSPNH6GYZLPJBY6X"}, {"8004": "7HYP4T4XTS4DXKCY"}, {"8001": "R8YY70F5MKN"}, {"8022": "69QGMN8PXWDYPNIF"}, {"8023": "IZDEGA8TFYXWRK9X"}], #Sếp
    "22614471": [{"8002": "7DXCUKKB6DVWDAQO"}, {"8006": "CEIN4X45I7ZHFEFU"}, {"8005": "UWJJOJLB85SO7LIZ"}, {"8003": "TSPNH6GYZLPJBY6X"}, {"8004": "7HYP4T4XTS4DXKCY"}, {"8001": "R8YY70F5MKN"}], #Lê Thị Liên
    "22616467": [{"8017": "EM4DYTEITCCYJNFU"}], #Hoàng Thị Thùy Linh
    "22615833": [{"8009": "9PAM7DIFW87DOBEU"}], #Chị Ngô Dung
    "22814414": [{"8019": "Z5LVOF4PRGXGTS9H"}], #Chị Bích Ngọc
    "22789191": [{"8014": "F6NZ5LRKWWGACYQ8"}], #Chị Lại Thị Nhàn
    "22833463": [{"8015": "QK8TEMKZMBYHPV6P"}], #Chị Thư
    "22636101":[{"8016": "IJP78949G69DKNHM"}], #Chị Thùy
    "22896992":[{"8013": "EY5H9DJNIVNFH6OR"}], #Huyền Trang
    "22911349":[{"8024": "R8YY70HCNRX"}], #Diễm Quỳnh
    "22889226":[{"8008": "CQIZKJ8P59AY7DHI"}], #Chị Ngọc Hà
    "22894754":[{"8007": "8HMN4T9575HAQWLN"}], #Chị Hải Yến
    "22889521":[{"8018": "PN59BMHYPFXCPN8T"}], #Chị Ngọc Mai
    "22735395":[{"8010": "EQLNQ8O7EQCQPFXG"}], #Chị Tâm
    "22897894":[{"8011": "YH9TSS7XCMPFZHNR"}], #Ngọc Anh
    "22846624":[{"8020": ""}], #Ngọc Ánh
    "22846622":[{"8021": "R8YY70F81TV"}], #Thu Trà
    "22891672":[{"8012": "MJZDFY896TMJBUPN"}], #Phạm Linh Chi
    "22907106":[{"8025": "R83Y50JZK6A"}], #Vân Anh
    "22862103":[{"8008": "CQIZKJ8P59AY7DHI"}], #Thằng đẻ ra ứng dụng
    "22858638":[{"8002": "7DXCUKKB6DVWDAQO"}, {"8005": "UWJJOJLB85SO7LIZ"}, {"8009": "9PAM7DIFW87DOBEU"}] #Phạm Huy dùng để test



}

@app.route('/api_get_list_users', methods=['POST', 'GET'])
def get_list_friend_new():
    data_body = request.form
    user_id = data_body.get('user_id')
    if user_id == "22495550":
        device_and_port = []
        for id in list(id_port.keys()):
            
            device_and_port += id_port[id]
    else:
        device_and_port = id_port[user_id]

    user_db = []
    for dp in device_and_port:
        ports = list(dp.keys())
        port = ports[0]
        device_id = dp[port]
        try:
            with open(f'C:/Zalo_CRM/Zalo_base/Zalo_data_login_path_{device_id}.json', 'r', encoding='utf-8') as f:
                zalo_data = json.load(f)
            with open(f'C:/Zalo_CRM/Zalo_base/device_status_{device_id}.json', 'r') as f:
                device_status = json.load(f)
        except Exception as e:
            print(e)
            pass
        for zalo in zalo_data:
            user_db.append({"num_phone_zalo": zalo['num_phone_zalo'], "status": zalo['status'], "user_name": zalo['name'], "avatar": zalo['ava'], "port": port})

    return jsonify({'user_db': user_db, 'update': device_status['update']})

#socketio.run(app, host="0.0.0.0", port=8000,
#                 debug=True, use_reloader=False)


socketio.run(
    app,
    host="0.0.0.0",
    port=8000,
    debug=True,
    use_reloader=False,
    certfile="ssl/fullchain.pem",
    keyfile="ssl/privkey.pem",
    server_side=True
)

    
    
