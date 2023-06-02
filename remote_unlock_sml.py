"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)

def ticket_remote_unlock(data1,data2):
    data2["ticket_id"]=data1["result"]["ticket_id"]
    print(data2)
    return data2


#tham số Tuya project
ACCESS_ID = "88rhdtkuvwuwvnf9sqfg"
ACCESS_KEY = "e3975867df94441195361e543bd45f85"
API_ENDPOINT = "https://openapi.tuyaus.com"
MQ_ENDPOINT = "wss://mqe.tuyaus.com:8285/"

# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

# Init openapi and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()


# cài đặt phương thức mở khóa từ xa
# command_set={
#     "remote_unlock_type": "remoteUnlockWithoutPwd",
#     "open": True
# }
# openapi.post("/v1.0/devices/6430387798f4abec248a/door-lock/remote-unlock/config",command_set)

command_remote_unlock={
    "ticket_id":"xxxxx"
}
#call api password ticket
password_ticket=openapi.post("/v1.0/devices/6430387798f4abec248a/door-lock/password-ticket")

new_command_remote_unlock=ticket_remote_unlock(password_ticket,command_remote_unlock)

# call api mo khoa tu xa
openapi.post("/v1.0/smart-lock/devices/6430387798f4abec248a/password-free/door-operate",new_command_remote_unlock)

# mở khóa từ xa
# command={
#     "ticket_id":'o765kdEO',
#  "open": True
# }
# openapi.post("/v1.0/smart-lock/devices/6430387798f4abec248a/password-free/door-operate",command)

# Init Message Queue
open_pulsar = TuyaOpenPulsar(
    ACCESS_ID, ACCESS_KEY, MQ_ENDPOINT, TuyaCloudPulsarTopic.PROD
)
# Add Message Queue listener
open_pulsar.add_message_listener(lambda msg: print(f"---\nexample receive: {msg}"))

# Start Message Queue
open_pulsar.start()

input()
# Stop Message Queue
open_pulsar.stop()
