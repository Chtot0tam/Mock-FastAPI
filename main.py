from typing import Union, Literal
from fastapi import FastAPI
from fastapi import responses
from pydantic import BaseModel
from fastapi import Header

app = FastAPI()


class BaseDevice(BaseModel):
    device_id: str
    owner: str
    room: str
    online: bool


class SocketDevice(BaseDevice):
    type: Literal["Socket"]
    power_w: float
    voltage: int


class WaterLeakSensor(BaseDevice):
    type: Literal["WaterLeakSensor"]
    leak_detected: bool
    battery: int


class TemperatureSensor(BaseDevice):
    type: Literal["TemperatureSensor"]
    temperature_c: float
    humidity: int


class LightDevice(BaseDevice):
    type: Literal["Light"]
    status: str
    brightness: int
    
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    
Device = Union[
    SocketDevice,
    WaterLeakSensor,
    TemperatureSensor,
    LightDevice
]

users: list[dict] = [
    {
        "username": "admin",
        "password": "admin123",
        "token": "admin-token",
        "role": "admin"
    },
    {
        "username": "user1",
        "password": "user123",
        "token": "user1-token",
        "role": "user"
    },
    {
        "username": "user2",
        "password": "user234",
        "token": "user2-token",
        "role": "user"
    }
]

devices: list[dict] = [
    {
        "id": 1,
        "device_id": "socket-01",
        "owner": "user1",
        "type": "Socket",
        "room": "Living Room",
        "online": True,
        "power_w": 42.5,
        "voltage": 230
    },
    {
        "id": 2,
        "device_id": "socket-02",
        "owner": "admin",
        "type": "Socket",
        "room": "Kitchen",
        "online": False,
        "power_w": 0,
        "voltage": 230
    },
    {
        "id": 3,
        "device_id": "water-01",
        "owner": "user1",
        "type": "WaterLeakSensor",
        "room": "Bathroom",
        "online": True,
        "leak_detected": False,
        "battery": 87
    },
    {
        "id": 4,
        "device_id": "water-02",
        "owner": "user2",
        "type": "WaterLeakSensor",
        "room": "Basement",
        "online": True,
        "leak_detected": True,
        "battery": 15,
        "warning": "WATER_LEAK_DETECTED"
    },
    {
        "id": 5,
        "device_id": "temp-01",
        "owner": "user1",
        "type": "TemperatureSensor",
        "room": "Bedroom",
        "online": True,
        "temperature_c": 23.4,
        "humidity": 45
    },
    {
        "id": 6,
        "device_id": "light-01",
        "owner": "admin",
        "type": "Light",
        "room": "Office",
        "online": True,
        "status": "On",
        "brightness": 80
    }
]


@app.get("/api/devices")
def get_devices():
    return devices


@app.get("/api/devices/{device_id}")
def get_device_by_id(device_id: int):

    for device in devices:
        if device["id"] == device_id:
            return device

    return responses.JSONResponse(
        status_code=404,
        content={"message": "Device not found"}
    )


@app.post("/api/devices")
def create_device(device: Device):

    new_device = {
        "id": len(devices) + 1,
        **device.model_dump()
    }

    devices.append(new_device)

    return responses.JSONResponse(
        status_code=201,
        content={
            "message": "Device created successfully",
            "device": new_device
        }
    )


@app.get("/api/devices/type/{device_type}")
def get_devices_by_type(device_type: str):

    matched_devices = []

    for device in devices:
        if device["type"].lower() == device_type.lower():
            matched_devices.append(device)

    if not matched_devices:
        return responses.JSONResponse(
            status_code=404,
            content={"message": "Devices not found"}
        )

    return matched_devices

@app.put("/api/devices/{device_id}")
def update_device(device_id: int, updated_device: Device):

    for index, device in enumerate(devices):

        if device["id"] == device_id:

            updated_data = {
                "id": device_id,
                **updated_device.model_dump()
            }

            devices[index] = updated_data

            return responses.JSONResponse(
                status_code=200,
                content={
                    "message": "Device updated successfully",
                    "device": updated_data
                }
            )

    return responses.JSONResponse(
        status_code=404,
        content={"message": "Device not found"}
    )
    
@app.delete("/api/devices/{device_id}")
def delete_device(device_id: int):

    for index, device in enumerate(devices):

        if device["id"] == device_id:

            deleted_device = devices.pop(index)

            return responses.JSONResponse(
                status_code=200,
                content={
                    "message": "Device deleted successfully",
                    "device": deleted_device
                }
            )

    return responses.JSONResponse(
        status_code=404,
        content={"message": "Device not found"}
    )
    
@app.post("/login")
def login(data: LoginRequest):

    for user in users:

        if (
            user["username"] == data.username
            and user["password"] == data.password
        ):

            return {
                "message": "Login successful",
                "token": user["token"],
                "role": user["role"]
            }

    return responses.JSONResponse(
        status_code=401,
        content={"message": "Invalid credentials"}
    )
    
@app.post("/register")
def register(data: RegisterRequest):

    for user in users:
        if user["username"] == data.username:

            return responses.JSONResponse(
                status_code=409,
                content={"message": "Username already exists"}
            )

    new_user = {
        "username": data.username,
        "password": data.password,
        "token": f"{data.username}-token",
        "role": "user"
    }

    users.append(new_user)

    return responses.JSONResponse(
        status_code=201,
        content={
            "message": "User registered successfully",
            "user": {
                "username": new_user["username"],
                "role": new_user["role"]
            }
        }
    )
    
