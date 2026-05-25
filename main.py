from typing import Union, Literal
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi import responses
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import secrets
import hashlib
import hmac
import json
import base64
import time

app = FastAPI()

# JWT-like token helpers 

SECRET_KEY = secrets.token_hex(32) 
TOKEN_TTL = 3600  # 1 час


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _sign(payload: dict) -> str:
    header = _b64(b'{"alg":"HS256","typ":"JWT"}')
    body = _b64(json.dumps(payload).encode())
    sig = hmac.new(SECRET_KEY.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
    return f"{header}.{body}.{_b64(sig)}"


def _verify(token: str) -> dict:
    try:
        header, body, sig = token.split(".")
        expected = _b64(
            hmac.new(SECRET_KEY.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(sig, expected):
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(body + "=="))
        if payload.get("exp", 0) < time.time():
            raise ValueError("token expired")
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Dependency: Get current user 

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    payload = _verify(credentials.credentials)
    username = payload.get("sub")
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user

# Models

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


Device = Union[SocketDevice, WaterLeakSensor, TemperatureSensor, LightDevice]

# BDs

users: list[dict] = [
    {"username": "admin",  "password": hash_password("admin123"), "role": "admin"},
    {"username": "user1",  "password": hash_password("user123"),  "role": "user"},
    {"username": "user2",  "password": hash_password("user234"),  "role": "user"},
]

devices: list[dict] = [
    {"id": 1, "device_id": "socket-01", "owner": "user1",  "type": "Socket",            "room": "Living Room", "online": True,  "power_w": 42.5, "voltage": 230},
    {"id": 2, "device_id": "socket-02", "owner": "admin",  "type": "Socket",            "room": "Kitchen",     "online": False, "power_w": 0,    "voltage": 230},
    {"id": 3, "device_id": "water-01",  "owner": "user1",  "type": "WaterLeakSensor",   "room": "Bathroom",    "online": True,  "leak_detected": False, "battery": 87},
    {"id": 4, "device_id": "water-02",  "owner": "user2",  "type": "WaterLeakSensor",   "room": "Basement",    "online": True,  "leak_detected": True,  "battery": 15, "warning": "WATER_LEAK_DETECTED"},
    {"id": 5, "device_id": "temp-01",   "owner": "user1",  "type": "TemperatureSensor", "room": "Bedroom",     "online": True,  "temperature_c": 23.4, "humidity": 45},
    {"id": 6, "device_id": "light-01",  "owner": "admin",  "type": "Light",             "room": "Office",      "online": True,  "status": "On", "brightness": 80},
]

# Auth 

@app.post("/login")
def login(data: LoginRequest):
    user = next((u for u in users if u["username"] == data.username), None)
    if not user or not hmac.compare_digest(user["password"], hash_password(data.password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = _sign({"sub": user["username"], "role": user["role"], "exp": int(time.time()) + TOKEN_TTL})
    return {"message": "Login successful", "token": token, "role": user["role"]}


@app.post("/register", status_code=201)
def register(data: RegisterRequest):
    if any(u["username"] == data.username for u in users):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    new_user = {"username": data.username, "password": hash_password(data.password), "role": "user"}
    users.append(new_user)
    return {"message": "User registered successfully", "user": {"username": data.username, "role": "user"}}

# Devices

@app.get("/api/devices")
def get_devices(_: dict = Depends(get_current_user)):
    """Only for authorized users."""
    return devices


@app.get("/api/devices/type/{device_type}")
def get_devices_by_type(device_type: str, _: dict = Depends(get_current_user)):
    """Only for authorized users."""
    matched = [d for d in devices if d["type"].lower() == device_type.lower()]
    if not matched:
        raise HTTPException(status_code=404, detail="Devices not found")
    return matched


@app.get("/api/devices/{device_id}")
def get_device_by_id(device_id: int, _: dict = Depends(get_current_user)):
    """Only for authorized users."""
    device = next((d for d in devices if d["id"] == device_id), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.post("/api/devices", status_code=201)
def create_device(device: Device, _: dict = Depends(require_admin)):
    """Only for administrators."""
    new_device = {"id": len(devices) + 1, **device.model_dump()}
    devices.append(new_device)
    return {"message": "Device created successfully", "device": new_device}


@app.put("/api/devices/{device_id}")
def update_device(device_id: int, updated_device: Device, _: dict = Depends(require_admin)):
    """Only for administrators."""
    for index, device in enumerate(devices):
        if device["id"] == device_id:
            updated_data = {"id": device_id, **updated_device.model_dump()}
            devices[index] = updated_data
            return {"message": "Device updated successfully", "device": updated_data}
    raise HTTPException(status_code=404, detail="Device not found")


@app.delete("/api/devices/{device_id}")
def delete_device(device_id: int, _: dict = Depends(require_admin)):
    """Only for administrators."""
    for index, device in enumerate(devices):
        if device["id"] == device_id:
            deleted_device = devices.pop(index)
            return {"message": "Device deleted successfully", "device": deleted_device}
    raise HTTPException(status_code=404, detail="Device not found")