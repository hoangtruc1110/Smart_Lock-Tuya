"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
#import datetime
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)
#thu vien datetime
from datetime import datetime
#thu vien excel
import openpyxl
import json
# pip3 install pycryptodome
#Các thư viện về giải mã,mã hóa, base64-hex
import base64
from Crypto.Cipher import AES
from Crypto.Util import Padding
from base64 import b64encode, b64decode
import codecs
import sqlite3


#tham số Tuya project
ACCESS_ID = "88rhdtkuvwuwvnf9sqfg"
ACCESS_KEY = "e3975867df94441195361e543bd45f85"
API_ENDPOINT = "https://openapi.tuyaus.com"
MQ_ENDPOINT = "wss://mqe.tuyaus.com:8285/"


#Các lệnh API :
#https://developer.tuya.com/en/docs/cloud/smart-door-lock?id=K9jgsgd4cgysr tong hop
#http://tool.chacuo.net/cryptaes/ : chuyen doi AES/EBC/PKCS7Padding

MK = int(input("Nhập mật khẩu tạm thời gồm 7 số, nhập 0 nếu không có nhu cầu: "))
tg=int(input("Nhập số ngày hết hạn mật khẩu, nhập 0 nếu không có nhu cầu : "))
Matkhau=str(MK)
new_time=tg*60*60*24

#Hàm mã hóa, đã chuyển kết quả từ base64 sang hex, data,key đã là base64
def aes_ecb_pkcs7_b64_encrypt(data, key):
    data = Padding.pad(data.encode('utf-8'), AES.block_size, 'pkcs7')
    aes = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    base_64=b64encode(aes.encrypt(data)).decode('utf-8')
    hex=b64decode(base_64).hex() #chuyển từ base64 sang hex
    return hex

#Hàm giải mã, đã chuyển data từ hex sang base64, key đã là base64
def aes_ecb_pkcs7_b64_decrypt(data, key):
    new_data=b64encode(bytes.fromhex(data)).decode() #chuyển data từ hex sang base64
    new_data = b64decode(new_data.encode('utf-8'))
    aes = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    return Padding.unpad(aes.decrypt(new_data), AES.block_size, 'pkcs7').decode('utf-8')


#hàm lọc dữ liệu event,status
def filter(value):
    lst=[]
    deviceId=value["devId"]
    lst.append(deviceId)
    productkey=value["productKey"]
    lst.append(productkey)
    code_battery=value["status"][0]["value"]
    lst.append(code_battery)
    code_action=value["status"][1]['code']
    lst.append(code_action)
    t = value["status"][1]['t']
    timestamp=datetime.fromtimestamp(t/1000)
    #print(timestamp)
    lst.append(str(timestamp))
    return lst
#
# #hàm gán biến vào Excel
# def callback(msg):
#     local = datetime.now() # goi ham thoi gian hien tai
#     data = json.loads(msg) # chuyen tin nhan tu dang string sang dict
#     print("Local:", local.strftime("%m/%d/%Y, %H:%M:%S"))
#     wb=openpyxl.load_workbook("Book1.xlsx")  #Goi excel Book1.xlsx
#     activesheet=wb.active
#     activesheet.title="Manage" # dat ten cho sheet 1 là Manage
#     #Gán các dữ liệu qua file Excel có sẵn
#     if filter(data)[0]:
#         for b in range(2,1000):
#             index="A"+str(b) #chuyen doi qua dang string
#             if activesheet[index].value== None: #kiểm tra dữ liệu đã có trong ô chưa
#                 activesheet[index].value=filter(data)[0] # nhập dữ liệu vào ô trống
#                 break
#     if filter(data)[1]:
#         for b in range(2, 1000):
#             index = "B"+ str(b)
#             if activesheet[index].value == None:
#                 activesheet[index].value = filter(data)[1]
#                 break
#     if filter(data)[2]:
#         for b in range(2, 1000):
#             index = "C" + str(b)
#             if activesheet[index].value == None:
#                 activesheet[index].value = filter(data)[2]
#                 break
#     if filter(data)[3]:
#         for b in range(2, 1000):
#             index = "D" + str(b)
#             if activesheet[index].value == None:
#                 activesheet[index].value = filter(data)[3]
#                 break
#     if filter(data)[4]:
#         for b in range(2, 1000):
#             index = "E" + str(b)
#             if activesheet[index].value == None:
#                 activesheet[index].value = filter(data)[4]
#                 break
#     wb.save("Book1.xlsx")


class employee:
    def __init__(self):
        self.infomations = information()


class information:
    def __init__(self):
        self.Device_Id = ""
        self.Product_Key= ""
        self.Battery_state=""
        self.Action=""
        self.Time=""


def insert_database(db, data):
    conn = sqlite3.connect(db + ".db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO "
        + db
        + " VALUES(:date , :local_url )",
        {
            "Device_Id": data.Device_Id,
            "Product_Key": data.Product_Key,
            "Battery_state": data.Battery_state,
            "Action": data.Action,
            "Time" : data.Time
        },
    )
    conn.commit()
    conn.close()



#tìm table có sẵn theo keyword
def search_path_database(db, key):
    conn = sqlite3.connect(db + ".db") #connect
    c = conn.cursor()
    c.execute("SELECT * FROM " + db + " WHERE date = :date", {"date": key})
    print(c.fetchall()) #in ra những gì mình chọn vào table
    conn.commit()
    conn.close()

#xóa tất cả data base
def delete_all_database(db):
    conn = sqlite3.connect(db + ".db")
    c = conn.cursor()
    c.execute("DELETE from " + db)
    conn.commit()
    conn.close()

#Tạo 1 data base mới
def create_database(name):
    conn = sqlite3.connect(name + ".db")
    c = conn.cursor()
    try:
        c.execute(
            """CREATE TABLE """
            + name
            + """(
            Device_Id text,
            Product_Key text
            Battery_state text,
            Action text,
            Time text,
            )"""
        )

    except Exception as e:
        #print(e)
        pass
    conn.commit()
    conn.close()


#Cập nhật trên db,db là database có sẵn
def add_employee(db, data1,data2):
    obj1 = employee()
    # delete_all_database(db)
    for key in data1:
        obj1.infomations.date = data1[key]
    for key in data2:
        obj1.infomations.local_url = data1[key]
    insert_database(db, obj1.infomations)
    search_path_database(db, "")



def callback(text):
    data = json.loads(text)  # chuyen tin nhan tu dang string sang dict
    print(data)
    create_database("Lock")
    obj1 = employee()
    if filter(data)[0]:
        obj1.infomations.Device_id=filter(data)[0]
    if filter(data)[1]:
        obj1.infomations.Product_Key=filter(data)[1]
    if filter(data)[2]:
        obj1.infomations.Battery_state=filter(data)[2]
    if filter(data)[3]:
        obj1.infomations.Action=filter(data)[3]
    if filter(data)[4]:
        obj1.infomations.Time=filter(data)[4]
    insert_database("Lock",obj1.infomations)


# Type of data is dict, data1: api password-ticket, data 2: command of api creative temp-pass
def get_ticket(data1,data2): #Ham gan vao new_command de doi temp_pass
    lst=[]
    ticket_id=data1["result"]["ticket_id"]
    lst.append(ticket_id)
    ticket_key = data1["result"]["ticket_key"]
    lst.append(ticket_key)
    t=data1["t"]
    t=int(t/1000)
    lst.append(t)
    data2["ticket_id"] = lst[0]
    data2["effective_time"] = lst[2]
    data2["invalid_time"]=lst[2]+new_time
    print(lst)
    new_key=aes_ecb_pkcs7_b64_decrypt(lst[1],ACCESS_KEY)
    new_pass=aes_ecb_pkcs7_b64_encrypt(Matkhau,new_key)
    data2["password"]=new_pass
    return data2

#kiểm tra thời gian thực
local = datetime.now()
time=local.strftime("%m/%d/%Y, %H:%M:%S")
print("Local:", local.strftime("%m/%d/%Y, %H:%M:%S"))

# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

# Init openapi and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

#send command
command_password = {
    "password": "a63a07c2cb2029e89efe8350979d71ef",
    "password_type": "ticket",
    "ticket_id": "8R0YxDcK",
    "effective_time": 1680582354,
    "invalid_time":   1680992354,
    "name":"test",
    "phone": "",
    "time_zone":"",
    "schedule_list":[{
        "effective_time": 720,
        "invalid_time": 1080,
        "working_day":  0
                    }],
    "relate_dev_list":["6430387798f4abec248a"]
}
command_remote_unlock={
    "ticket_id":"xxxxx"
}

#openapi.get("v1.0/iot-03/devices/6430387798f4abec248a")
# Call any API from Tuya
password_ticket=openapi.post("/v1.0/devices/6430387798f4abec248a/door-lock/password-ticket")

#Điền command mới theo ticket_id hiện tại
new_command_password=get_ticket(password_ticket,command_password)
print(new_command_password)

#Call api đổi mật khẩu theo mật khẩu đã nhập
openapi.post("/v1.0/devices/6430387798f4abec248a/door-lock/temp-password",new_command_password)

#response = openapi.get("/v1.0/statistics-datas-survey", dict())
# Init Message Queue
open_pulsar = TuyaOpenPulsar(
    ACCESS_ID, ACCESS_KEY, MQ_ENDPOINT, TuyaCloudPulsarTopic.PROD
)

# Add Message Queue listener
#open_pulsar.add_message_listener(lambda msg: print(f"---\nexample receive: {msg}"))
open_pulsar.add_message_listener(lambda msg: callback(msg))
print()

# Start Message Queue
open_pulsar.start()

input()
# Stop Message Queue
open_pulsar.stop()
