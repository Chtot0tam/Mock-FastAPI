from typing import Optional
from fastapi import FastAPI
from fastapi import responses
from pydantic import BaseModel

class Device(BaseModel):
    device_id: str
    owner: str
    type: str
    room: str
    online: bool

    # Socket fields
    power_w: Optional[float] = None
    voltage: Optional[int] = None

    # Water sensor fields
    leak_detected: Optional[bool] = None
    battery: Optional[int] = None

    # Temperature sensor fields
    temperature_c: Optional[float] = None
    humidity: Optional[int] = None

    # Light fields
    status: Optional[str] = None
    brightness: Optional[int] = None

app = FastAPI()

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
def get_devices_by_id(device_id: int):
    
    for device in devices:
        if device["id"] == device_id:
            return device
    return responses.JSONResponse(status_code=404, content={"message": "Device not found"})
@app.post("/api/devices")
def create_device(device: Device):

    new_device = {
        "id": len(devices) + 1,
        **device.model_dump(exclude_none=True)
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
