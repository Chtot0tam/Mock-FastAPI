# Mock-FastAPI

# OverView

This project is a simple implementation of IoT Devices Environment. It is made for training API testing and security checks. It runs on local host and has several intended vulnerabilities to find.

# How to set up FastAPI

1. Download [Python](https://www.python.org/downloads/?utm_source=chatgpt.com)
1. Download [VS Code] (https://code.visualstudio.com/download)
2. Install FastAPI: Open VS Code and insert the command in terminal ```pip install fastapi uvicorn```
3. Import this repository and open as a project in VS Code. 
4. In the terminal insert ```py -m uvicorn main:app --reload```
5. The terminal gives you the URL like ```http://127.0.0.1:8000```
6. In the browser insert your URL and ```/docs``` in the end to open Swagger documentation. 

# Description

This FastAPI has several HTTP methods including registration and login.  
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

# Tests
### How to test
To implement tests follow the instructions:
1. Download [Postman](https://www.postman.com/downloads/)
2. Import the Postman.json file in Postman (on the left bar press on "..." icon and import the file.) 
3. Run the tests
### CRUD Test Cases
1. 200: Get all devices method response is array and not zero. 
2. 200: A certain device has certain properties.
3. 404: Get non-existent device.
4. 200: Get device by type and verify.
5. 404: Get invalid device type.
6. 201: Create socket device. 
7. 201: Create watersensor.
8. 422: Create a socket with missing required fields.
9. 422: Create a device with invalid datatype.
10. 200: Update device
11. 404: Update non-existing device. 
12. 200: Delete existing device.
13. 404: Delete non-existing device.
### Auth Tests
1. 200: Successful login
2. 401: Invalid password
3. 401: Non existing user
### Registration Test Cases
1. 201: Successful registration.
2. 409: Duplicate username.
3. 422: Missing credential.
