#!/usr/bin/env python3
"""
DHT22 Environmental Monitoring System - FastAPI Backend
간단한 DHT22 온습도 모니터링 서버

기능:
- FastAPI 기본 서버
- WebSocket 실시간 통신
- DHT22 시뮬레이터 연동
- 실시간 데이터 브로드캐스팅
- 웹 대시보드
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# 시뮬레이터 패키지 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# DHT22 계산 함수들
def calculate_heat_index(temp_c: float, humidity: float) -> float:
    """체감온도 계산"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c: float, humidity: float) -> float:
    """이슬점 계산"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)

class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔌 Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

class DHT22Simulator:
    """DHT22 시뮬레이터"""
    
    def __init__(self):
        self.sequence = 0
        self.mode = "NORMAL"
    
    def get_sensor_data(self) -> dict:
        """시뮬레이션 데이터 생성"""
        import random
        
        if self.mode == "NORMAL":
            temperature = 22.5 + random.uniform(-2.5, 2.5)
            humidity = 50.0 + random.uniform(-10.0, 10.0)
        elif self.mode == "HOT_DRY":
            temperature = 35.0 + random.uniform(-5.0, 5.0)
            humidity = 30.0 + random.uniform(-10.0, 10.0)
        elif self.mode == "COLD_WET":
            temperature = 10.0 + random.uniform(-5.0, 5.0)
            humidity = 80.0 + random.uniform(-10.0, 10.0)
        else:
            temperature = 25.0 + random.uniform(-5.0, 5.0)
            humidity = 60.0 + random.uniform(-15.0, 15.0)
        
        # 범위 제한
        temperature = max(-40, min(80, temperature))
        humidity = max(0, min(100, humidity))
        
        heat_index = calculate_heat_index(temperature, humidity)
        dew_point = calculate_dew_point(temperature, humidity)
        
        self.sequence += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "heat_index": heat_index,
            "dew_point": dew_point,
            "sequence_number": self.sequence,
            "sensor_status": "ok",
            "simulation_mode": self.mode
        }

# FastAPI 앱 생성
app = FastAPI(title="DHT22 Environmental Monitoring", version="1.0.0")

# 전역 객체들
manager = ConnectionManager()
simulator = DHT22Simulator()

@app.get("/")
async def root():
    """루트 페이지 - 실시간 대시보드"""
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DHT22 Environmental Monitoring</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .panel {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #dc3545;
        }
        .status-indicator.connected {
            background-color: #28a745;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-primary {
            background-color: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background-color: #0056b3;
        }
        .btn-danger {
            background-color: #dc3545;
            color: white;
        }
        .btn-success {
            background-color: #28a745;
            color: white;
        }
        .measurement {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }
        .metric {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            color: white;
        }
        .metric.temperature {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        }
        .metric.humidity {
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        }
        .metric.heat-index {
            background: linear-gradient(135deg, #ffe66d 0%, #ffcc02 100%);
            color: #333;
        }
        .metric.dew-point {
            background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%);
            color: #333;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric-label {
            font-size: 12px;
            opacity: 0.9;
        }
        .data-display {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            font-family: 'Courier New', monospace;
        }
        .log {
            height: 200px;
            max-height: 200px;
            overflow-y: auto;
            background-color: #000;
            color: #00ff00;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            white-space: pre-wrap;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .stat-item {
            text-align: center;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #495057;
        }
        .stat-label {
            font-size: 11px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌡️ DHT22 Environmental Monitoring System</h1>
        <p>Real-time Temperature & Humidity Monitoring</p>
    </div>

    <div class="container">
        <div class="panel">
            <h3>📡 Connection Control</h3>
            <div class="status">
                <div class="status-indicator" id="wsStatus"></div>
                <span id="wsStatusText">Disconnected</span>
            </div>
            <div class="controls">
                <button class="btn-primary" onclick="connectWebSocket()">Connect</button>
                <button class="btn-danger" onclick="disconnectWebSocket()">Disconnect</button>
                <button class="btn-success" onclick="clearLog()">Clear Log</button>
            </div>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value" id="messageCount">0</div>
                    <div class="stat-label">Messages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="dataRate">0.0</div>
                    <div class="stat-label">Rate/sec</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="uptime">00:00</div>
                    <div class="stat-label">Uptime</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="errorCount">0</div>
                    <div class="stat-label">Errors</div>
                </div>
            </div>
        </div>

        <div class="panel">
            <h3>🌡️ Real-time Environmental Data</h3>
            <div class="measurement">
                <div class="metric temperature">
                    <div class="metric-value" id="temperature">--</div>
                    <div class="metric-label">Temperature (°C)</div>
                </div>
                <div class="metric humidity">
                    <div class="metric-value" id="humidity">--</div>
                    <div class="metric-label">Humidity (%RH)</div>
                </div>
                <div class="metric heat-index">
                    <div class="metric-value" id="heatIndex">--</div>
                    <div class="metric-label">Heat Index (°C)</div>
                </div>
                <div class="metric dew-point">
                    <div class="metric-value" id="dewPoint">--</div>
                    <div class="metric-label">Dew Point (°C)</div>
                </div>
            </div>
            <div class="data-display">
                <strong>Last Data:</strong><br>
                <span id="lastData">No data received</span>
            </div>
        </div>
    </div>

    <div class="panel">
        <h3>📋 Message Log</h3>
        <div class="log" id="messageLog"></div>
    </div>

    <script>
        let ws = null;
        let messageCount = 0;
        let errorCount = 0;
        let startTime = null;

        function connectWebSocket() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                log('Already connected', 'warning');
                return;
            }

            ws = new WebSocket('ws://localhost:8000/ws');
            startTime = new Date();

            ws.onopen = function(event) {
                log('Connected to DHT22 server', 'success');
                document.getElementById('wsStatus').classList.add('connected');
                document.getElementById('wsStatusText').textContent = 'Connected';
            };

            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    updateDisplay(data);
                    messageCount++;
                    updateStats();
                } catch (e) {
                    log('Error parsing data: ' + e.message, 'error');
                    errorCount++;
                }
            };

            ws.onclose = function(event) {
                log('Connection closed', 'warning');
                document.getElementById('wsStatus').classList.remove('connected');
                document.getElementById('wsStatusText').textContent = 'Disconnected';
            };

            ws.onerror = function(error) {
                log('WebSocket error: ' + error, 'error');
                errorCount++;
            };
        }

        function disconnectWebSocket() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function updateDisplay(data) {
            document.getElementById('temperature').textContent = data.temperature;
            document.getElementById('humidity').textContent = data.humidity;
            document.getElementById('heatIndex').textContent = data.heat_index;
            document.getElementById('dewPoint').textContent = data.dew_point;
            
            document.getElementById('lastData').textContent = 
                `Temp: ${data.temperature}°C, Humidity: ${data.humidity}%RH, Heat Index: ${data.heat_index}°C`;
            
            log(`📊 T:${data.temperature}°C H:${data.humidity}%RH HI:${data.heat_index}°C DP:${data.dew_point}°C`);
        }

        function updateStats() {
            document.getElementById('messageCount').textContent = messageCount;
            document.getElementById('errorCount').textContent = errorCount;
            
            if (startTime) {
                const uptime = Math.floor((new Date() - startTime) / 1000);
                const minutes = Math.floor(uptime / 60);
                const seconds = uptime % 60;
                document.getElementById('uptime').textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                const rate = uptime > 0 ? (messageCount / uptime).toFixed(1) : '0.0';
                document.getElementById('dataRate').textContent = rate;
            }
        }

        function log(message, type = 'info') {
            const logElement = document.getElementById('messageLog');
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : '#00ff00';
            
            logElement.innerHTML += `<span style="color: ${color}">[${timestamp}] ${message}</span>\\n`;
            logElement.scrollTop = logElement.scrollHeight;
        }

        function clearLog() {
            document.getElementById('messageLog').innerHTML = '';
        }

        // 자동 연결
        window.onload = function() {
            connectWebSocket();
        };
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 엔드포인트"""
    await manager.connect(websocket)
    try:
        while True:
            # 1초마다 센서 데이터 전송
            data = simulator.get_sensor_data()
            await manager.broadcast(json.dumps(data))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/current")
async def get_current_data():
    """현재 센서 데이터 조회"""
    return simulator.get_sensor_data()

@app.post("/api/simulation/mode")
async def set_simulation_mode(mode: str):
    """시뮬레이션 모드 변경"""
    valid_modes = ["NORMAL", "HOT_DRY", "COLD_WET", "EXTREME_HOT", "EXTREME_COLD"]
    if mode in valid_modes:
        simulator.mode = mode
        return {"status": "success", "mode": mode}
    else:
        return {"status": "error", "message": "Invalid mode"}

if __name__ == "__main__":
    print("🚀 DHT22 Environmental Monitoring Server Starting...")
    print("📊 Dashboard: http://localhost:8000")
    print("🔌 WebSocket: ws://localhost:8000/ws")
    print("📡 API: http://localhost:8000/api/current")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")