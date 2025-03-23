import requests
#This is an Agent to make an http call to an api \

apiBaseurl = ""
path1 = "metro/cities"
path2 = "metro/search"
#Get request
response1 = requests.get(apiBaseurl + path1)
print("Get resposne")
status = response1.status_code

if status != 200:
    print("api failed")
else:
    print("Status is 200")

print(response1.json())

print("===========================================================")

#post request 

payload = {
     "city": "std:044",
    "endingStation": "SGE|0109",
    "startingStation": "SGM|0115",
    "txnId": ""
}
headers = {
"AuthToken":"",
"Channel_Name":"MOBILE_APP",
"BusinessUnit":"METRO",
"Content-Type":"application/json"

}

response2 = requests.post(apiBaseurl + path2, json=payload, headers=headers)
print("post response")
status = response2.status_code
if status != 200:
    print("api failed")
else:
    print("Status is 200")

print(response2.json())









