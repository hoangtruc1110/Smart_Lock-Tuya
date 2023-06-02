"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)

#tham số Tuya project
ACCESS_ID = "88rhdtkuvwuwvnf9sqfg"
ACCESS_KEY = "e3975867df94441195361e543bd45f85"
API_ENDPOINT = "https://openapi.tuyaus.com"
MQ_ENDPOINT = "wss://mqe.tuyaus.com:8285/"

button=int(input("Mở rèm chọn 1, đóng rèm chọn 0 : "))

# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

openapi.get('/v1.0/iot-03/devices/status?device_ids=ebdf2051227157cb51dvsu')#id thiet bi lay trong phan project
