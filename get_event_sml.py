"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
#import datetime
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)
from datetime import datetime
import json
import sqlite3


#tham số Tuya project
ACCESS_ID = "88rhdtkuvwuwvnf9sqfg"
ACCESS_KEY = "e3975867df94441195361e543bd45f85"
API_ENDPOINT = "https://openapi.tuyaus.com"
MQ_ENDPOINT = "wss://mqe.tuyaus.com:8285/"

#Các lệnh API :
#https://developer.tuya.com/en/docs/cloud/smart-door-lock?id=K9jgsgd4cgysr tong hop

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
        + " VALUES(:Device_Id , :Product_Key , :Battery_state , :Action , :Time )",
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
    print(lst)
    return lst

def callback(text):
    data = json.loads(text)  # chuyen tin nhan tu dang string sang dict
    print(data)
    obj1 = employee()
    create_database("Lock")
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


# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

# Init openapi and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

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
