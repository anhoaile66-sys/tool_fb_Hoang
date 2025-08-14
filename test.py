for _ in range(0):
    print("hello world")

def modify_dict(data):
    data["value"] = 100

def change_dict(data):
    data = {"value": 200}

original = {"value": 1}
modify_dict(original)
# print(original)  # Kết quả: {'value': 100} (đã bị thay đổi)

hehe = {"value": 2}
change_dict(hehe)
# print(hehe)  # Kết quả: {'value': 100} (đã bị thay đổi)

import json

with open("user_account.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for acc in data:
    acc["name"] = None

for acc in data:
    del acc["account"]
    del acc["name"]

print(data)