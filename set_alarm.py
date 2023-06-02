"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)
from datetime import datetime
import time

#tham số Tuya project
ACCESS_ID = "88rhdtkuvwuwvnf9sqfg"
ACCESS_KEY = "e3975867df94441195361e543bd45f85"
API_ENDPOINT = "https://openapi.tuyaus.com"
MQ_ENDPOINT = "wss://mqe.tuyaus.com:8285/"

button=int(input("Mở rèm chọn 1, đóng rèm chọn 0 : "))
set_time_day=int(input("Nhap ngay bao thuc, bao thuc moi ngay nhap 0 : "))
set_time_h=int(input("Nhap gio mo: "))
set_time_m=int(input("Nhap phut mo: "))

if 0 < set_time_h <10:
    set_time_h='0'+str(set_time_h)
if 0 < set_time_m < 10:
    set_time_m='0'+str(set_time_m)
if 0 < set_time_day < 10:
    set_time_day='0'+str(set_time_day)

# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

curtain_command={
  "commands": [
    {
      "code": "thay the thanh ten chuc nang thiet bi ",#vi du: switch_led
      "value": True
    }
  ]
}

if button==1:
    curtain_command['commands'][0]['value']= True
if button==0:
    curtain_command['commands'][0]['value']= False
print(curtain_command)
#response=openapi.post("/v1.0/iot-03/devices/{device_id}/commands",curtain_command)
print("Giờ hiện tại: ",str(datetime.now())[11:19])

check=0
while True:
    if set_time_day==0:
        if str(datetime.now())[11:19]==str(set_time_h)+':'+str(set_time_m)+':00':
            # continue
        #     if check == 0:
        #         print("bao thuc")
        #         check = 1
        # else:
        #     check=0
            print("Bao thuc")
            time.sleep(1)
        # openapi.post("/v1.0/iot-03/devices/{device_id}/commands",curtain_command)
    if str(datetime.now())[8:10]==str(set_time_day):
        if str(datetime.now())[11:19] == str(set_time_h) + ':' + str(set_time_m) + ':00':
            # continue
            #     if check == 0:
            #         print("bao thuc")
            #         check = 1
            # else:
            #     check=0
            print("Bao thuc")
            time.sleep(1)
            break

