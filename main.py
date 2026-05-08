from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "IoT Security Lab API"
    }

@app.get("/devices")
def get_devices():
    return [
        {
            "id": "socket-01",
            "type": "Socket",
            "online": True
        },
        {
            "id": "socket-02",
            "type": "Socket",
            "online": False
        },
        {
            "id": "sensor-01",
            "type": "WaterLeakSensor",
            "online": True
        }
    ]