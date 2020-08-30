import requests
from threading import Thread
import time

url = "http://ec2-18-217-1-165.us-east-2.compute.amazonaws.com/punch"
myjson = {"bag_id": "001", "score": "1000"}

def request():
    x = requests.post(url, json = myjson)
    print(x.text)

def main():
    while True:
        t = Thread(target=request)
        t.start()
        time.sleep(.02)

main()