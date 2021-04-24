import requests
import time
from threading import Thread
import socket

url = "http://192.168.100.137:3000/punches"

def request(myjson):
    x = requests.post(url, json = myjson)
    print('sent')

while True:
    myobj = {"bag_id":"001","score":"99","count":"99"}
    t = Thread(target=request, args=(myobj,))
    t.start()
    time.sleep(.01)