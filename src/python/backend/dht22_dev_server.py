# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
DHT22 Environmental Monitoring System - Development Server
"""
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import uvicorn
# Assume climate_calculator has the necessary functions
from climate_calculator import calculate_dew_point, calculate_heat_index
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


def setup_logging() -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(
        log_dir / f"dht22_dev_{datetime.now().strftime('%Y%m%d')}.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)


logger = setup_logging()


class DHT22Simulator:
    def __init__(self) -> None:
        self.mode = "NORMAL"
        self.modes = {
            "NORMAL": {"temp_range": (20, 28), "hum_range": (40, 60)},
            "HOT_DRY": {"temp_range": (30, 38), "hum_range": (20, 35)},
        }

    def set_mode(self, mode: str) -> None:
        if mode in self.modes:
            self.mode = mode

    def get_sensor_data(self) -> dict:
        temp_range = self.modes[self.mode]["temp_range"]
        hum_range = self.modes[self.mode]["hum_range"]
        temp = round(time.time() % 10 + temp_range[0], 2)
        humidity = round(time.time() % 20 + hum_range[0], 2)
        heat_index = calculate_heat_index(temp, humidity)
        dew_point = calculate_dew_point(temp, humidity)
        return {
            "timestamp": datetime.now().isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "heat_index": heat_index,
            "dew_point": dew_point,
            "mode": self.mode,
        }


simulator = DHT22Simulator()
app = FastAPI()


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    with open("dashboard.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = simulator.get_sensor_data()
            await manager.broadcast(json.dumps(data))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
