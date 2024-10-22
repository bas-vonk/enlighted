import json

import requests

user = "sjj.vonk@gmail.com"
password = "zem@rnd7tnj2TQD4uqa"
envoy_serial = "122151085606"
data = {"user[email]": user, "user[password]": password}
response = requests.post(
    "http://enlighten.enphaseenergy.com/login/login.json?", data=data
)
response_data = json.loads(response.text)
data = {
    "session_id": response_data["session_id"],
    "serial_num": envoy_serial,
    "username": user,
}
response = requests.post("http://entrez.enphaseenergy.com/tokens", json=data)
token_raw = response.text
print(token_raw)
