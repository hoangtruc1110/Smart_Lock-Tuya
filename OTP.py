"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)

# pip3 install pycryptodome
#Các thư viện về giải mã,mã hóa, base64-hex
import base64
from Crypto.Cipher import AES
from Crypto.Util import Padding
from base64 import b64encode, b64decode
import math, random
import json

#tham số Tuya project
ACCESS_ID = "88rhdtkuvwuwvnf9sqfg"
ACCESS_KEY = "e3975867df94441195361e543bd45f85"
API_ENDPOINT = "https://openapi.tuyaus.com"
MQ_ENDPOINT = "wss://mqe.tuyaus.com:8285/"

new_time=60*5 #OTP có thời hạn là 5p, tính luôn delay sau khi sinh ra mật khẩu do cloud

def generateOTP():
    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    OTP = ""
    # length of password can be changed
    # by changing value in range
    for i in range(7):
        OTP += digits[math.floor(random.random() * 10)]
    print("OTP có thời hạn trong vòng 5 phút: ",OTP)
    return OTP

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

# Type of data is dict, data1: api password-ticket, data 2: command of api creative command for remote_unlock
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
    new_pass=aes_ecb_pkcs7_b64_encrypt(generateOTP(),new_key)
    data2["password"]=new_pass
    return data2

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

# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

# Init openapi and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

#openapi.get("v1.0/iot-03/devices/6430387798f4abec248a")
# Call any API from Tuya
password_ticket=openapi.post("/v1.0/devices/6430387798f4abec248a/door-lock/password-ticket")

#Điền command mới theo ticket_id hiện tại
new_command_password=get_ticket(password_ticket,command_password)
#print(new_command_password)

#Call api đổi mật khẩu theo mật khẩu đã nhập
openapi.post("/v1.0/devices/6430387798f4abec248a/door-lock/temp-password",new_command_password)

# Call any API from Tuya
#response = openapi.get("/v1.0/statistics-datas-survey", dict())

# Init Message Queue
open_pulsar = TuyaOpenPulsar(
    ACCESS_ID, ACCESS_KEY, MQ_ENDPOINT, TuyaCloudPulsarTopic.PROD
)
# Add Message Queue listener
# open_pulsar.add_message_listener(lambda msg: print(f"---\nexample receive: {msg}"))
#
# # Start Message Queue
# open_pulsar.start()
#
# input()
# # Stop Message Queue
# open_pulsar.stop()

