# -*- coding: utf-8 -*-
"""
DHT22 환경 모니터링 웹 대시보드 (FastAPI 기반)
- WebSocket을 통한 실시간 데이터 전송
- REST API 엔드포인트 제공
- DHT22 센서 시뮬레이터 내장
"""
import asyncio
import json
import random
from datetime import datetime
from typing import Any, Dict, List

from climate_calculator import (
    calculate_dew_point,
    calculate_discomfort_index,
    calculate_heat_index,
    get_discomfort_level,
)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


class DHT22Simulator:
    """DHT22 센서 데이터 생성을 위한 시뮬레이터"""

    def __init__(self) -> None:
        self.mode = "NORMAL"
        self.modes = {
            "NORMAL": {"temp_range": (20, 28), "hum_range": (40, 60)},
            "HOT_DRY": {"temp_range": (30, 38), "hum_range": (20, 35)},
            "COLD_WET": {"temp_range": (5, 15), "hum_range": (70, 85)},
        }

    def set_mode(self, mode: str) -> bool:
        if mode in self.modes:
            self.mode = mode
            return True
        return False

    def get_sensor_data(self) -> Dict[str, Any]:
        temp_range = self.modes[self.mode]["temp_range"]
        hum_range = self.modes[self.mode]["hum_range"]
        temp = random.uniform(*temp_range)
        humidity = random.uniform(*hum_range)
        temp = max(-40.0, min(80.0, temp))
        humidity = max(0.0, min(100.0, humidity))
        heat_index = calculate_heat_index(temp, humidity)
        dew_point = calculate_dew_point(temp, humidity)
        discomfort_index = calculate_discomfort_index(temp, humidity)
        discomfort_level = get_discomfort_level(discomfort_index)
        return {
            "timestamp": datetime.now().isoformat(),
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "heat_index": round(heat_index, 2),
            "dew_point": round(dew_point, 2),
            "discomfort_index": round(discomfort_index, 2),
            "discomfort_level": discomfort_level,
            "mode": self.mode,
        }


simulator = DHT22Simulator()


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("dashboard.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
            data = simulator.get_sensor_data()
            await manager.broadcast(json.dumps(data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("클라이언트 연결 해제")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
