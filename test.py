import requests

url = "http://ec2-18-217-1-165.us-east-2.compute.amazonaws.com/punch"
myjson = {"bag_id": "001", "score": "1000"}

x = requests.post(url, json = myjson)

print(x.text)