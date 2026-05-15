# Mock-FastAPI

# OverView
This project is a simple implementation of IoT Devices Environment. It is made for training API testing and security checks. It runs local host and has several intended vulnerabilities to find.

# SetUp  
0. Download [Python](https://www.python.org/downloads/?utm_source=chatgpt.com)
1. Download [VS Code] (https://code.visualstudio.com/download)
2. Install FastAPI: Open VS Code and insert the command in terminal ```pip install fastapi uvicorn```
3. Import this repository and open as a project in VS Code. 
4. In the terminal insert ```uvicorn main:app --reload```
5. The terminal gives you the URL like ```http://127.0.0.1:8000```
6. In the browser insert your URL and ```/docs``` in the end to open documentation. 
### Description
This project has several HTTP methods including registration and login.  
1. Get ```api/devices``` return the list of devices and their details.  
Example:  
```json"id": 1,
    "device_id": "socket-01",
    "owner": "user1",
    "type": "Socket",
    "room": "Living Room",
    "online": true,
    "power_w": 42.5,
    "voltage": 230
```
2. Post ```api/devices``` allows to create a new device.
3. Get ```api/devices/{device_id}``` returns information about a certain device. 
4. Put ```api/devices{device_id}``` allows to change the information about a device.
5. Delete ```api/devices/{device_id}``` to delete a device.
6. Get ```api/devices/type/{device_type}``` get the list of devices with a certain type. 
7. Post ```/login```
8. Post ```/register```

