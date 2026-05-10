from fastapi import FastAPI
from fastapi import responses
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

@app.get("/")
def home():
    return {"Hello": "World"}

@app.get("/api/devices")
def get_devices():
    return devices