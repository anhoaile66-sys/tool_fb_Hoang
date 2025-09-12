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
    "22614471": [{"8002": "7DXCUKKB6DVWDAQO"}, {"8006": "CEIN4X45I7ZHFEFU"}, {"8005": "UWJJOJLB85SO7LIZ"}, {"8003": "TSPNH6GYZLPJBY6X"}],
    "22615833": [{"8009": "9PAM7DIFW87DOBEU"}], #Chị Ngô Dung
    "22814414": [{"8019": "Z5LVOF4PRGXGTS9H"}], #Chị Bích Ngọc
    "22789191": [{"8014": "F6NZ5LRKWWGACYQ8"}], #Chị Lại Thị Nhàn
    "22833463": [{"8003": "TSPNH6GYZLPJBY6X"}], #Chị Thư
    "22636101":[], #Chị Thùy
    "22896992":[{"8013": "EY5H9DJNIVNFH6OR"}], #Chị Huyền Trang
    "22889226":[{"8008": "CQIZKJ8P59AY7DHI"}], #Chị Ngọc Hà
    "22894754":[{"8007": "8HMN4T9575HAQWLN"}], #Chị Hải Yến
    "22889521":[{"8018": "PN59BMHYPFXCPN8T"}], #Chị Ngọc Mai
    "22735395":[{"8010": ""}], #Chị Tâm
    "22897894":[{"8011": ""}], #Ngọc Anh
    "22862103":[{"8002": "7DXCUKKB6DVWDAQO"}, {"8008": "CQIZKJ8P59AY7DHI"}, {"8005": "UWJJOJLB85SO7LIZ"}] #Thằng đẻ ra ứng dụng


}

@app.route('/api_get_list_users', methods=['POST', 'GET'])
def get_list_friend_new():
    data_body = request.form
    user_id = data_body.get('user_id')
    #if user_id == "22862103":
    #    device_and_port = []
    #    for id in list(id_port.keys()):
            
    #        device_and_port += id_port[id]
    #else:
    device_and_port = id_port[user_id]

    user_db = []
    for dp in device_and_port:
        ports = list(dp.keys())
        port = ports[0]
        device_id = dp[port]
        try:
            with open(f'C:/Zalo_CRM/Zalo_base/Zalo_data_login_path_{device_id}.json', 'r', encoding='utf-8') as f:
                zalo_data = json.load(f)
        except Exception as e:
            print(e)
            pass
        for zalo in zalo_data:
            user_db.append({"num_phone_zalo": zalo['num_phone_zalo'], "user_name": zalo['name'], "avatar": zalo['ava'], "port": port})

    return jsonify({'user_db': user_db})

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

    
    
