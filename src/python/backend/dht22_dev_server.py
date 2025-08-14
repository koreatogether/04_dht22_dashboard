#!/usr/bin/env python3
"""
DHT22 Environmental Monitoring System - Development Server
개발용 DHT22 온습도 모니터링 서버 (로깅 강화 버전)

기능:
- 구조화된 로깅 시스템
- 개발 모드 디버깅 지원
- 실시간 로그 모니터링
- 성능 메트릭 수집
- 자동 리로드 지원
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# 로깅 설정
def setup_logging():
    """개발용 로깅 설정"""
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 로그 포맷터
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 파일 핸들러 (전체 로그)
    file_handler = logging.FileHandler(
        log_dir / f"dht22_dev_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 에러 전용 핸들러
    error_handler = logging.FileHandler(
        log_dir / f"dht22_errors_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    return logging.getLogger(__name__)

# 로거 초기화
logger = setup_logging()

# DHT22 계산 함수들
def calculate_heat_index(temp_c: float, humidity: float) -> float:
    """체감온도 계산"""
    logger.debug(f"체감온도 계산: 온도={temp_c}°C, 습도={humidity}%")
    
    if temp_c < 27:
        result = temp_c
        logger.debug(f"온도가 27°C 미만이므로 체감온도 = 실제온도: {result}°C")
        return result
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    result = round((hi - 32) * 5/9, 1)
    
    logger.debug(f"체감온도 계산 완료: {result}°C (화씨: {temp_f}°F → {hi}°F)")
    return result

def calculate_dew_point(temp_c: float, humidity: float) -> float:
    """이슬점 계산"""
    logger.debug(f"이슬점 계산: 온도={temp_c}°C, 습도={humidity}%")
    
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    result = round((b * alpha) / (a - alpha), 1)
    
    logger.debug(f"이슬점 계산 완료: {result}°C")
    return result

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "websocket_connections": 0,
            "data_points_generated": 0,
            "errors_total": 0,
            "start_time": time.time()
        }
        self.logger = logging.getLogger(f"{__name__}.PerformanceMonitor")
    
    def increment_requests(self):
        self.metrics["requests_total"] += 1
        self.logger.debug(f"총 요청 수: {self.metrics['requests_total']}")
    
    def increment_websocket_connections(self):
        self.metrics["websocket_connections"] += 1
        self.logger.info(f"WebSocket 연결 수 증가: {self.metrics['websocket_connections']}")
    
    def decrement_websocket_connections(self):
        self.metrics["websocket_connections"] -= 1
        self.logger.info(f"WebSocket 연결 수 감소: {self.metrics['websocket_connections']}")
    
    def increment_data_points(self):
        self.metrics["data_points_generated"] += 1
        if self.metrics["data_points_generated"] % 100 == 0:
            self.logger.info(f"생성된 데이터 포인트: {self.metrics['data_points_generated']}")
    
    def increment_errors(self):
        self.metrics["errors_total"] += 1
        self.logger.warning(f"총 오류 수: {self.metrics['errors_total']}")
    
    def get_metrics(self) -> Dict:
        uptime = time.time() - self.metrics["start_time"]
        return {
            **self.metrics,
            "uptime_seconds": round(uptime, 2),
            "requests_per_second": round(self.metrics["requests_total"] / uptime, 2) if uptime > 0 else 0
        }

class ConnectionManager:
    """WebSocket 연결 관리자 (로깅 강화)"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.active_connections: List[WebSocket] = []
        self.performance_monitor = performance_monitor
        self.logger = logging.getLogger(f"{__name__}.ConnectionManager")
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.performance_monitor.increment_websocket_connections()
        
        client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
        self.logger.info(f"클라이언트 연결됨: {client_info}, 총 연결 수: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.performance_monitor.decrement_websocket_connections()
            
            client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
            self.logger.info(f"클라이언트 연결 해제됨: {client_info}, 총 연결 수: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        if not self.active_connections:
            self.logger.debug("브로드캐스트할 연결이 없음")
            return
        
        self.logger.debug(f"{len(self.active_connections)}개 연결에 메시지 브로드캐스트")
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                self.logger.warning(f"메시지 전송 실패: {e}")
                disconnected.append(connection)
                self.performance_monitor.increment_errors()
        
        for connection in disconnected:
            self.disconnect(connection)

class DHT22Simulator:
    """DHT22 시뮬레이터 (로깅 강화)"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.sequence = 0
        self.mode = "NORMAL"
        self.performance_monitor = performance_monitor
        self.logger = logging.getLogger(f"{__name__}.DHT22Simulator")
        
        self.logger.info(f"DHT22 시뮬레이터 초기화 완료, 모드: {self.mode}")
    
    def set_mode(self, mode: str):
        """시뮬레이션 모드 변경"""
        old_mode = self.mode
        self.mode = mode
        self.logger.info(f"시뮬레이션 모드 변경: {old_mode} → {mode}")
    
    def get_sensor_data(self) -> Dict:
        """시뮬레이션 데이터 생성"""
        import random
        
        self.logger.debug(f"센서 데이터 생성 시작, 모드: {self.mode}")
        
        try:
            if self.mode == "NORMAL":
                temperature = 22.5 + random.uniform(-2.5, 2.5)
                humidity = 50.0 + random.uniform(-10.0, 10.0)
            elif self.mode == "HOT_DRY":
                temperature = 35.0 + random.uniform(-5.0, 5.0)
                humidity = 30.0 + random.uniform(-10.0, 10.0)
            elif self.mode == "COLD_WET":
                temperature = 10.0 + random.uniform(-5.0, 5.0)
                humidity = 80.0 + random.uniform(-10.0, 10.0)
            elif self.mode == "EXTREME_HOT":
                temperature = 45.0 + random.uniform(-5.0, 5.0)
                humidity = 20.0 + random.uniform(-10.0, 10.0)
            elif self.mode == "EXTREME_COLD":
                temperature = -5.0 + random.uniform(-10.0, 10.0)
                humidity = 75.0 + random.uniform(-15.0, 15.0)
            else:
                temperature = 25.0 + random.uniform(-5.0, 5.0)
                humidity = 60.0 + random.uniform(-15.0, 15.0)
            
            # 범위 제한
            temperature = max(-40, min(80, temperature))
            humidity = max(0, min(100, humidity))
            
            # 환경 지수 계산
            heat_index = calculate_heat_index(temperature, humidity)
            dew_point = calculate_dew_point(temperature, humidity)
            
            self.sequence += 1
            self.performance_monitor.increment_data_points()
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
                "heat_index": heat_index,
                "dew_point": dew_point,
                "sequence_number": self.sequence,
                "sensor_status": "ok",
                "simulation_mode": self.mode
            }
            
            self.logger.debug(f"센서 데이터 생성 완료: T={data['temperature']}°C, H={data['humidity']}%, HI={data['heat_index']}°C")
            return data
            
        except Exception as e:
            self.logger.error(f"센서 데이터 생성 중 오류: {e}")
            self.performance_monitor.increment_errors()
            raise

# FastAPI 앱 생성
app = FastAPI(
    title="DHT22 Environmental Monitoring - Development Server",
    version="1.0.0-dev",
    description="개발용 DHT22 온습도 모니터링 서버 (로깅 강화)",
    debug=True
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 객체들
performance_monitor = PerformanceMonitor()
manager = ConnectionManager(performance_monitor)
simulator = DHT22Simulator(performance_monitor)

# 미들웨어: 요청 로깅
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    logger.info(f"요청 시작: {request.method} {request.url}")
    performance_monitor.increment_requests()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"요청 완료: {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")
    
    return response

@app.get("/")
async def root():
    """루트 페이지 - 개발용 대시보드"""
    logger.info("루트 페이지 요청")
    
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DHT22 Development Server</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .dev-badge {
            background: #FF9800;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-top: 10px;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
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
            flex-wrap: wrap;
        }
        button {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            font-size: 12px;
        }
        .btn-primary { background-color: #007bff; color: white; }
        .btn-danger { background-color: #dc3545; color: white; }
        .btn-success { background-color: #28a745; color: white; }
        .btn-warning { background-color: #ffc107; color: #212529; }
        .btn-info { background-color: #17a2b8; color: white; }
        
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
        .metric.temperature { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); }
        .metric.humidity { background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); }
        .metric.heat-index { background: linear-gradient(135deg, #ffe66d 0%, #ffcc02 100%); color: #333; }
        .metric.dew-point { background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%); color: #333; }
        
        .metric-value {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric-label {
            font-size: 11px;
            opacity: 0.9;
        }
        
        .log {
            height: 300px;
            max-height: 300px;
            overflow-y: auto;
            background-color: #000;
            color: #00ff00;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            white-space: pre-wrap;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
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
            font-size: 16px;
            font-weight: bold;
            color: #495057;
        }
        .stat-label {
            font-size: 10px;
            color: #6c757d;
        }
        
        .mode-selector {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }
        .mode-btn {
            padding: 5px 10px;
            font-size: 11px;
            border-radius: 15px;
        }
        .mode-btn.active {
            background-color: #28a745;
            color: white;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌡️ DHT22 Environmental Monitoring</h1>
        <p>Development Server with Enhanced Logging</p>
        <div class="dev-badge">DEVELOPMENT MODE</div>
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
            </div>
        </div>

        <div class="panel">
            <h3>🎛️ Simulation Control</h3>
            <div class="mode-selector">
                <button class="mode-btn btn-success active" onclick="setMode('NORMAL')">Normal</button>
                <button class="mode-btn btn-warning" onclick="setMode('HOT_DRY')">Hot Dry</button>
                <button class="mode-btn btn-info" onclick="setMode('COLD_WET')">Cold Wet</button>
                <button class="mode-btn btn-danger" onclick="setMode('EXTREME_HOT')">Extreme Hot</button>
                <button class="mode-btn btn-primary" onclick="setMode('EXTREME_COLD')">Extreme Cold</button>
            </div>
            <div class="controls">
                <button class="btn-info" onclick="getMetrics()">Get Metrics</button>
                <button class="btn-warning" onclick="testAPI()">Test API</button>
            </div>
            <div id="metricsDisplay" style="font-size: 12px; margin-top: 10px;"></div>
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
        </div>
    </div>

    <div class="panel">
        <h3>📋 Development Log</h3>
        <div class="log" id="messageLog"></div>
    </div>

    <script>
        let ws = null;
        let messageCount = 0;
        let startTime = null;
        let currentMode = 'NORMAL';

        function connectWebSocket() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                log('Already connected', 'warning');
                return;
            }

            ws = new WebSocket('ws://localhost:8001/ws');
            startTime = new Date();

            ws.onopen = function(event) {
                log('🔗 Connected to DHT22 development server', 'success');
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
                    log('❌ Error parsing data: ' + e.message, 'error');
                }
            };

            ws.onclose = function(event) {
                log('🔌 Connection closed', 'warning');
                document.getElementById('wsStatus').classList.remove('connected');
                document.getElementById('wsStatusText').textContent = 'Disconnected';
            };

            ws.onerror = function(error) {
                log('💥 WebSocket error: ' + error, 'error');
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
            
            log(`📊 [${data.simulation_mode}] T:${data.temperature}°C H:${data.humidity}%RH HI:${data.heat_index}°C DP:${data.dew_point}°C`);
        }

        function updateStats() {
            document.getElementById('messageCount').textContent = messageCount;
            
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

        async function setMode(mode) {
            try {
                const response = await fetch('/api/simulation/mode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode: mode })
                });
                const result = await response.json();
                
                if (result.status === 'success') {
                    currentMode = mode;
                    log(`🎛️ Simulation mode changed to: ${mode}`, 'success');
                    
                    // 버튼 상태 업데이트
                    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
                    event.target.classList.add('active');
                } else {
                    log(`❌ Failed to change mode: ${result.message}`, 'error');
                }
            } catch (e) {
                log(`💥 Error changing mode: ${e.message}`, 'error');
            }
        }

        async function getMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const metrics = await response.json();
                
                const display = document.getElementById('metricsDisplay');
                display.innerHTML = `
                    <strong>Server Metrics:</strong><br>
                    Requests: ${metrics.requests_total}<br>
                    WebSocket: ${metrics.websocket_connections}<br>
                    Data Points: ${metrics.data_points_generated}<br>
                    Errors: ${metrics.errors_total}<br>
                    Uptime: ${metrics.uptime_seconds}s<br>
                    RPS: ${metrics.requests_per_second}
                `;
                
                log('📈 Server metrics updated', 'info');
            } catch (e) {
                log(`💥 Error getting metrics: ${e.message}`, 'error');
            }
        }

        async function testAPI() {
            try {
                const response = await fetch('/api/current');
                const data = await response.json();
                log(`🧪 API Test - Current data: T:${data.temperature}°C H:${data.humidity}%RH`, 'info');
            } catch (e) {
                log(`💥 API Test failed: ${e.message}`, 'error');
            }
        }

        function log(message, type = 'info') {
            const logElement = document.getElementById('messageLog');
            const timestamp = new Date().toLocaleTimeString();
            const colors = {
                'error': '#ff6b6b',
                'success': '#51cf66',
                'warning': '#ffd43b',
                'info': '#74c0fc'
            };
            const color = colors[type] || '#00ff00';
            
            logElement.innerHTML += `<span style="color: ${color}">[${timestamp}] ${message}</span>\\n`;
            logElement.scrollTop = logElement.scrollHeight;
        }

        function clearLog() {
            document.getElementById('messageLog').innerHTML = '';
            log('🧹 Log cleared', 'info');
        }

        // 자동 연결
        window.onload = function() {
            log('🚀 DHT22 Development Server Dashboard loaded', 'success');
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
        logger.info("WebSocket 연결이 정상적으로 종료됨")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        manager.disconnect(websocket)
        performance_monitor.increment_errors()

@app.get("/api/current")
async def get_current_data():
    """현재 센서 데이터 조회"""
    logger.debug("현재 센서 데이터 요청")
    try:
        data = simulator.get_sensor_data()
        logger.debug(f"현재 센서 데이터 반환: {data}")
        return data
    except Exception as e:
        logger.error(f"현재 센서 데이터 조회 오류: {e}")
        performance_monitor.increment_errors()
        raise HTTPException(status_code=500, detail="센서 데이터 조회 실패")

@app.post("/api/simulation/mode")
async def set_simulation_mode(request: dict):
    """시뮬레이션 모드 변경"""
    mode = request.get("mode", "NORMAL")
    logger.info(f"시뮬레이션 모드 변경 요청: {mode}")
    
    valid_modes = ["NORMAL", "HOT_DRY", "COLD_WET", "EXTREME_HOT", "EXTREME_COLD"]
    if mode in valid_modes:
        simulator.set_mode(mode)
        logger.info(f"시뮬레이션 모드 변경 완료: {mode}")
        return {"status": "success", "mode": mode}
    else:
        logger.warning(f"잘못된 시뮬레이션 모드 요청: {mode}")
        performance_monitor.increment_errors()
        raise HTTPException(status_code=400, detail="Invalid simulation mode")

@app.get("/api/metrics")
async def get_metrics():
    """서버 성능 메트릭 조회"""
    logger.debug("서버 메트릭 요청")
    try:
        metrics = performance_monitor.get_metrics()
        logger.debug(f"서버 메트릭 반환: {metrics}")
        return metrics
    except Exception as e:
        logger.error(f"서버 메트릭 조회 오류: {e}")
        performance_monitor.increment_errors()
        raise HTTPException(status_code=500, detail="메트릭 조회 실패")

@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    logger.debug("헬스 체크 요청")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-dev"
    }

if __name__ == "__main__":
    logger.info("🚀 DHT22 개발 서버 시작 중...")
    logger.info("📊 대시보드: http://localhost:8001")
    logger.info("🔌 WebSocket: ws://localhost:8001/ws")
    logger.info("📡 API: http://localhost:8001/api/current")
    logger.info("📈 메트릭: http://localhost:8001/api/metrics")
    logger.info("💚 헬스체크: http://localhost:8001/api/health")
    
    uvicorn.run(
        "dht22_dev_server:app", 
        host="0.0.0.0", 
        port=8001,
        log_level="info",
        reload=True,  # 개발 모드: 파일 변경 시 자동 리로드
        access_log=True
    )