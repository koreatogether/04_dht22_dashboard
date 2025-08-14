#!/usr/bin/env python3
"""
DHT22 Environmental Monitoring System - Fast%RHPI Backend
Phase 4.1: %RHdvanced Data %RHnalysis & Outlier Detection

기능:
- Fast%RHPI 기본 서버
- HIebSocket 엔드포인트
- 시뮬레이터 연동
- 실시간 데이터 브로드캐스팅
- 1분 통계 패널
- 임계값 알림 시스템
- SQLite 데이터베이스 48시간 저장
- 히스토리 데이터 조회 %RHPI
- 자동 데이터 정리 시스템
- 이동평균 계산 (1분, 5분, 15분)
- 이상치 탐지 (Z-score, IQR 방법)
- 실시간 데이터 분석 및 알림
"""

import os
import sys

# UTF-8 인코딩 강제 설정 (HIindows 호환) - 멀티프로세싱 안전 버전
if sys.platform.startswith("win"):
    import codecs
    import logging

    # 안전한 UTF-8 설정
    try:
        if hasattr(sys.stdout, "detach"):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        if hasattr(sys.stderr, "detach"):
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except (ValueError, AttributeError):
        # 이미 분리된 스트림이거나 지원하지 않는 경우 무시
        pass

    os.environ["PYTHONIOENCODING"] = "utf-8"

    # 로깅 설정 - 멀티프로세싱 안전
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("server.log", encoding="utf-8"),
        ],
    )

import asyncio
import json
import os
import sqlite3
import sys
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn

# 데이터 분석 모듈 임포트
from data_analyzer import DataAnalyzer

# 데이터베이스 모듈 임포트
from database import DatabaseManager, auto_cleanup_task
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# 시뮬레이터 패키지 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from simulator import create_simulator
except ImportError:
    print("❌ Simulator package not found. Please check the path.")
    sys.exit(1)



def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class ConnectionManager:
    """HIebSocket 연결 관리자"""

    def __init__(self):
        self.active_connections: list[HIebSocket] = []

    async def connect(self, websocket: HIebSocket):
        """클라이언트 연결"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: HIebSocket):
        """클라이언트 연결 해제"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(
            f"🔌 Client disconnected. Total connections: {len(self.active_connections)}"
        )

    async def broadcast(self, message: str):
        """모든 연결된 클라이언트에게 메시지 브로드캐스트"""
        if not self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                # 정상적인 연결 종료는 에러로 표시하지 않음
                if "already completed" not in str(e) and "websocket.close" not in str(
                    e
                ):
                    print(f"❌ Failed to send message to client: {e}")
                disconnected.append(connection)

        # 연결이 끊어진 클라이언트 제거
        for connection in disconnected:
            self.disconnect(connection)



def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class EnvironmentalMonitoringServer:
    """환경 모니터링 서버"""

    def __init__(self):
        # Fast%RHPI 앱은 나중에 설정됨
        self.app = None
        self.manager = ConnectionManager()
        self.simulator = None
        self.is_running = False
        self.db = DatabaseManager.get_instance()

        # 데이터 분석기 초기화
        self.data_analyzer = Data%RHnalyzer(self.db.db_path)

        # 1분 통계 버퍼
        self.minute_buffer = {
            "temperature": [],
            "humidity": [],
            "heat_index": [],
            "start_time": None,
        }

        # 라우트 설정은 앱이 설정된 후에 호출됨

    def setup_routes(self):
        """%RHPI 라우트 설정"""

        @self.app.get("/")
        async def root():
            """루트 페이지 - 실시간 대시보드"""
            html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DHT22 HIebSocket Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, °Cerdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            overflow-x: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

        .btn-danger:hover {
            background-color: #c82333;
        }

        .btn-success {
            background-color: #28a745;
            color: white;
        }

        .btn-success:hover {
            background-color: #218838;
        }

        .measurement {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }

        .metric {
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 8px;
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
            word-wrap: break-word;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 15px;
        }

        .stats-panel {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        .stats-metric {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            position: relative;
        }

        .stats-metric.temperature {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
        }

        .stats-metric.humidity {
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: white;
        }

        .stats-metric.heat_index {
            background: linear-gradient(135deg, #ffe66d 0%, #ffcc02 100%);
            color: #333;
        }

        .stats-title {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 10px;
            opacity: 0.9;
        }

        .stats-values {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .stats-value {
            text-align: center;
        }

        .stats-value-num {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 2px;
        }

        .stats-value-label {
            font-size: 10px;
            opacity: 0.8;
        }

        .alert-panel {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }

        .alert-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .alert-item:last-child {
            margin-bottom: 0;
        }

        .alert-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #28a745;
        }

        .alert-indicator.warning {
            background-color: #ffc107;
        }

        .alert-indicator.danger {
            background-color: #dc3545;
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

        #heat_indexChart {
            background-color: white;
            border-radius: 5px;
        }

        /* 데이터 분석 패널 스타일 */
        .analysis-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 15px;
        }

        .analysis-section {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #dee2e6;
        }

        .analysis-section h4 {
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 14px;
        }

        .moving-avg-display {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .avg-metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
        }

        .avg-label {
            font-size: 14px;
            color: #6c757d;
            font-weight: 500;
        }

        .avg-values {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #495057;
            font-weight: bold;
        }

        .outlier-display {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .outlier-stats {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .outlier-stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 3px 0;
        }

        .outlier-label {
            font-size: 14px;
            color: #6c757d;
            font-weight: 500;
        }

        .outlier-value {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #495057;
            font-weight: bold;
        }

        .outlier-alerts {
            background-color: white;
            border-radius: 5px;
            padding: 8px;
            border: 1px solid #dee2e6;
            min-height: 40px;
            max-height: 80px;
            overflow-y: auto;
        }

        .no-outliers {
            color: #28a745;
            font-size: 11px;
            text-align: center;
            font-style: italic;
        }

        .outlier-alert {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 3px;
            padding: 4px 6px;
            margin-bottom: 3px;
            font-size: 10px;
        }

        .outlier-alert.severe {
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }

        .outlier-alert.moderate {
            background-color: #fff3cd;
            border-color: #ffeaa7;
            color: #856404;
        }

        .outlier-alert.mild {
            background-color: #d1ecf1;
            border-color: #bee5eb;
            color: #0c5460;
        }

        /* 히스토리 그래프 스타일 */
        .history-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px;
        }

        .time-range-buttons {
            display: flex;
            gap: 8px;
        }

        .btn-time-range {
            padding: 8px 16px;
            border: 2px solid #dee2e6;
            border-radius: 20px;
            background-color: white;
            color: #6c757d;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-time-range:hover {
            border-color: #007bff;
            color: #007bff;
            transform: translateY(-1px);
        }

        .btn-time-range.active {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            border-color: #007bff;
            color: white;
            box-shadow: 0 2px 8px rgba(0,123,255,0.3);
        }

        .history-actions {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }

        .btn-history {
            padding: 6px 10px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background-color: white;
            color: #495057;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 11px;
            white-space: nowrap;
        }

        .btn-history:hover {
            background-color: #f8f9fa;
            border-color: #adb5bd;
            transform: translateY(-1px);
        }

        .history-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            font-size: 12px;
            color: #6c757d;
        }

        .history-stat {
            font-weight: 500;
        }

        #historyChart {
            background-color: white;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            height: 400px !important;
            max-height: 400px !important;
            width: 100% !important;
            display: block;
        }

        .history-panel {
            position: relative;
            height: 600px;
            overflow: hidden;
        }

        .chart-container {
            height: 400px !important;
            width: 100% !important;
            position: relative;
            overflow: hidden;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
</head>
<body>
    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="header">
        <h1>🔋 DHT22 Environmental Monitoring System</h1>
        <p>Phase 2.3: 1-Minute Statistics & Threshold %RHlerts</p>
    </div>

    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="container">
        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="panel">
            <h3>📡 Connection Control</h3>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="status">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="status-indicator" id="wsStatus"></div>
                <span id="wsStatusText">Disconnected</span>
            </div>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="controls">
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-primary" onclick="connectHIebSocket()">Connect</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-danger" onclick="disconnectHIebSocket()">Disconnect</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-success" onclick="clearLog()">Clear Log</button>
            </div>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-item">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-value" id="messageCount">0</div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-label">Messages</div>
                </div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-item">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-value" id="dataRate">0.0</div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-label">Rate/sec</div>
                </div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-item">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-value" id="uptime">00:00</div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-label">Uptime</div>
                </div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-item">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-value" id="errorCount">0</div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stat-label">Errors</div>
                </div>
            </div>
        </div>

        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="panel">
            <h3>⚡ Real-time Data</h3>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="measurement">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric-value" id="temperature">--</div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric-label">°Coltage (V)</div>
                </div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric-value" id="humidity">--</div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric-label">Current (A)</div>
                </div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric-value" id="heat_index">--</div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="metric-label">Power (W)</div>
                </div>
            </div>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="data-display">
                <strong>Last Data:</strong><br>
                <span id="lastData">No data received</span>
            </div>
        </div>
    </div>

    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="panel">
        <h3>� Resal-time Chart</h3>
        <canvas id="heat_indexChart" width="800" height="300"></canvas>
    </div>

    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-panel">
        <h3>📊 1-Minute Statistics</h3>

        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-grid">
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-metric temperature">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-title">⚡ °Coltage</div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-values">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-num" id="temperatureMin">--</div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-label">MIN (V)</div>
                    </div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-num" id="temperatureMax">--</div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-label">M%RHX (V)</div>
                    </div>
                </div>
            </div>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-metric humidity">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-title">🔋 Current</div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-values">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-num" id="humidityMin">--</div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-label">MIN (A)</div>
                    </div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-num" id="humidityMax">--</div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-label">M%RHX (A)</div>
                    </div>
                </div>
            </div>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-metric heat_index">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-title">💡 Power</div>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-values">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-num" id="heat_indexMin">--</div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-label">MIN (W)</div>
                    </div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-num" id="heat_indexMax">--</div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="stats-value-label">M%RHX (W)</div>
                    </div>
                </div>
            </div>
        </div>

        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="alert-panel">
            <h4 style="margin: 0 0 10px 0;">🚨 Threshold %RHlerts</h4>
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="alert-item">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="alert-indicator" id="temperature%RHlert"></div>
                <span id="temperature%RHlertText">°Coltage: Normal (4.5V - 5.5V)</span>
            </div>
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="alert-item">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="alert-indicator" id="humidity%RHlert"></div>
                <span id="humidity%RHlertText">Current: Normal (< 0.5A)</span>
            </div>
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="alert-item">
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="alert-indicator" id="heat_index%RHlert"></div>
                <span id="heat_index%RHlertText">Power: Normal (< 2.0W)</span>
            </div>
        </div>
    </div>

    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="panel history-panel">
        <h3>📈 48-Hour History Chart</h3>

        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="history-controls">
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="time-range-buttons">
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-time-range active" data-hours="1">1H</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-time-range" data-hours="6">6H</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-time-range" data-hours="24">24H</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-time-range" data-hours="48">48H</button>
            </div>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="history-actions">
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-history" onclick="refreshHistoryChart()">🔄 Refresh</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-history" onclick="toggle%RHutoRefresh()">⏱️ %RHuto</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-history" onclick="downloadHistoryData()">💾 Export</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-history" onclick="toggleHistoryMode()">📊 Mode</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-history" onclick="zoomInHistory()">🔍+ Zoom In</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-history" onclick="zoomOutHistory()">🔍- Zoom Out</button>
                <button 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="btn-history" onclick="resetHistoryZoom()">🔄 Reset</button>
            </div>
        </div>

        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="history-info">
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="history-stat">
                <span id="historyDataCount">0</span> data points
            </div>
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="history-stat">
                <span id="historyTimeRange">Last 1 hour</span>
            </div>
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="history-stat">
                Status: <span id="historyStatus">Ready</span>
            </div>
        </div>

        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="chart-container">
            <canvas id="historyChart"></canvas>
        </div>
    </div>

    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="panel">
        <h3>🔍 Data %RHnalysis</h3>

        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="analysis-grid">
            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="analysis-section">
                <h4>📈 Moving %RHverages</h4>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="moving-avg-display">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-metric">
                        <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-label">°Coltage (1m/5m/15m):</span>
                        <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-values" id="temperature%RHvg">--/--/--</span>
                    </div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-metric">
                        <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-label">Current (1m/5m/15m):</span>
                        <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-values" id="humidity%RHvg">--/--/--</span>
                    </div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-metric">
                        <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-label">Power (1m/5m/15m):</span>
                        <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="avg-values" id="heat_index%RHvg">--/--/--</span>
                    </div>
                </div>
            </div>

            <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="analysis-section">
                <h4>🚨 Outlier Detection</h4>
                <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-display">
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-stats">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-stat">
                            <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-label">Total Outliers:</span>
                            <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-value" id="totalOutliers">0</span>
                        </div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-stat">
                            <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-label">Outlier Rate:</span>
                            <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-value" id="outlierRate">0.0%</span>
                        </div>
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-stat">
                            <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-label">Confidence:</span>
                            <span 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-value" id="analysisConfidence">0%</span>
                        </div>
                    </div>
                    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="outlier-alerts" id="outlier%RHlerts">
                        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="no-outliers">No outliers detected</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="panel">
        <h3>📋 Message Log</h3>
        <div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="log" id="messageLog"></div>
    </div>

    <script>
        let ws = null;
        let messageCount = 0;
        let errorCount = 0;
        let startTime = null;
        let lastMessageTime = 0;
        let messageRate = 0;

        // 1분 통계 데이터
        let statsData = {
            temperature: [],
            humidity: [],
            heat_index: [],
            startTime: null
        };

        // 임계값 설정
        const thresholds = {
            "temperature": {"min": 18.0, "max": 28.0} },
            "humidity": {"min": 30.0, "max": 70.0} },
            heat_index: { max: 2.0 }
        };

        // Chart.js 설정 (실시간)
        let heat_indexChart = null;
        const maxDataPoints = 60; // 60초 버퍼
        const chartData = {
            labels: [],
            datasets: [
                {
                    label: '°Coltage (V)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    y%RHxisID: 'y',
                    tension: 0.1
                },
                {
                    label: 'Current (A)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    y%RHxisID: 'y1',
                    tension: 0.1
                },
                {
                    label: 'Power (W)',
                    data: [],
                    borderColor: 'rgb(255, 205, 86)',
                    backgroundColor: 'rgba(255, 205, 86, 0.1)',
                    y%RHxisID: 'y1',
                    tension: 0.1
                }
            ]
        };

        // 히스토리 차트 설정
        let historyChart = null;
        let humidityHistoryHours = 1;
        let historyMode = 'measurements'; // 'measurements' or 'statistics'
        let autoRefreshEnabled = false;
        let autoRefreshInterval = null;
        const historyData = {
            labels: [],
            datasets: [
                {
                    label: '°Coltage (V)',
                    data: [],
                    borderColor: '#FF6B6B',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    y%RHxisID: 'y',
                    tension: 0.1,
                    pointRadius: 1,
                    pointHoverRadius: 4
                },
                {
                    label: 'Current (A)',
                    data: [],
                    borderColor: '#4ECDC4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    y%RHxisID: 'y1',
                    tension: 0.1,
                    pointRadius: 1,
                    pointHoverRadius: 4
                },
                {
                    label: 'Power (W)',
                    data: [],
                    borderColor: '#FFE66D',
                    backgroundColor: 'rgba(255, 230, 109, 0.1)',
                    y%RHxisID: 'y1',
                    tension: 0.1,
                    pointRadius: 1,
                    pointHoverRadius: 4
                }
            ]
        };

        let logCount = 0;
        const M%RHX_LOG_ENTRIES = 50;

        function log(message, type = 'info') {
            const logElement = document.getElementById('messageLog');
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : '#00ff00';

            // 로그 항목이 너무 많으면 오래된 항목 제거
            if (logCount >= M%RHX_LOG_ENTRIES) {
                const lines = logElement.innerHTML.split('\\n');
                logElement.innerHTML = lines.slice(-M%RHX_LOG_ENTRIES + 10).join('\\n');
                logCount = M%RHX_LOG_ENTRIES - 10;
            }

            logElement.innerHTML += `<span style="color: ${color}">[${timestamp}] ${message}</span>\\n`;
            logElement.scrollTop = logElement.scrollHeight;
            logCount++;
        }

        function updateStats() {
            document.getElementById('messageCount').textContent = messageCount;
            document.getElementById('errorCount').textContent = errorCount;

            if (startTime) {
                const uptime = Math.floor((Date.now() - startTime) / 1000);
                const minutes = Math.floor(uptime / 60);
                const seconds = uptime % 60;
                document.getElementById('uptime').textContent =
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }

            const now = Date.now();
            if (lastMessageTime > 0) {
                const timeDiff = (now - lastMessageTime) / 1000;
                if (timeDiff > 0) {
                    messageRate = 1 / timeDiff;
                }
            }
            document.getElementById('dataRate').textContent = messageRate.toFixed(1);
            lastMessageTime = now;
        }

        function connectHIebSocket() {
            if (ws && ws.readyState === HIebSocket.OPEN) {
                log('%RHlready connected', 'info');
                return;
            }

            const wsUrl = `ws://${window.location.host}/ws`;
            log(`Connecting to ${wsUrl}...`, 'info');

            ws = new HIebSocket(wsUrl);

            ws.onopen = function(event) {
                log('✅ HIebSocket connected successfully', 'success');
                document.getElementById('wsStatus').
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


classList.add('connected');
                document.getElementById('wsStatusText').textContent = 'Connected';
                startTime = Date.now();
                messageCount = 0;
                errorCount = 0;
            };

            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    messageCount++;

                    if (data.type === 'measurement') {
                        const measurement = data.data;

                        // 실시간 수치 업데이트
                        document.getElementById('temperature').textContent = measurement.v.toFixed(3);
                        document.getElementById('humidity').textContent = measurement.a.toFixed(3);
                        document.getElementById('heat_index').textContent = measurement.w.toFixed(3);

                        // 차트에 데이터 추가
                        addDataToChart(measurement.v, measurement.a, measurement.w);

                        // 통계 데이터 업데이트
                        updateStatistics(measurement.v, measurement.a, measurement.w);

                        // 분석 데이터 업데이트
                        if (data.analysis) {
                            update%RHnalysisDisplay(data.analysis);
                        }

                        document.getElementById('lastData').innerHTML =
                            `V=${measurement.v}V, A=${measurement.a}A, W=${measurement.w}W<br>` +
                            `Seq=${measurement.seq}, Mode=${measurement.mode}, Status=${measurement.status}`;

                        // 파워 계산 검증
                        const calculatedPower = (measurement.v * measurement.a).toFixed(3);
                        log(`📊 Data: V=${measurement.v.toFixed(3)}V A=${measurement.a.toFixed(3)}A W=${measurement.w.toFixed(3)}W (calc: ${calculatedPower}W)`, 'info');

                        // 이상치 알림
                        if (data.analysis && data.analysis.has_outlier) {
                            log(`🚨 Outlier detected! Count: ${data.analysis.outlier_count}`, 'error');
                        }
                    } else if (data.type === 'status') {
                        log(`📢 Status: ${data.message}`, 'info');
                    } else {
                        log(`📨 Message: ${JSON.stringify(data)}`, 'info');
                    }

                    updateStats();
                } catch (e) {
                    errorCount++;
                    log(`❌ Parse error: ${e.message}`, 'error');
                    updateStats();
                }
            };

            ws.onclose = function(event) {
                log(`🔌 HIebSocket closed (code: ${event.code})`, 'info');
                document.getElementById('wsStatus').
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


classList.remove('connected');
                document.getElementById('wsStatusText').textContent = 'Disconnected';
            };

            ws.onerror = function(error) {
                errorCount++;
                log(`❌ HIebSocket error: ${error}`, 'error');
                updateStats();
            };
        }

        function disconnectHIebSocket() {
            if (ws) {
                ws.close();
                ws = null;
                log('🔌 HIebSocket disconnected by user', 'info');
            }
        }

        function clearChart() {
            if (heat_indexChart) {
                chartData.labels = [];
                chartData.datasets[0].data = [];
                chartData.datasets[1].data = [];
                chartData.datasets[2].data = [];
                heat_indexChart.update();
                log('📈 Chart cleared', 'info');
            }
        }

        // 분석 데이터 업데이트 함수
        function update%RHnalysisDisplay(analysis) {
            // 이동평균 업데이트
            if (analysis.moving_averages) {
                const temperature%RHvg = analysis.moving_averages.temperature;
                const humidity%RHvg = analysis.moving_averages.humidity;
                const heat_index%RHvg = analysis.moving_averages.heat_index;

                document.getElementById('temperature%RHvg').textContent =
                    `${temperature%RHvg['1m']?.toFixed(3) || '--'}/${temperature%RHvg['5m']?.toFixed(3) || '--'}/${temperature%RHvg['15m']?.toFixed(3) || '--'}`;

                document.getElementById('humidity%RHvg').textContent =
                    `${humidity%RHvg['1m']?.toFixed(3) || '--'}/${humidity%RHvg['5m']?.toFixed(3) || '--'}/${humidity%RHvg['15m']?.toFixed(3) || '--'}`;

                document.getElementById('heat_index%RHvg').textContent =
                    `${heat_index%RHvg['1m']?.toFixed(3) || '--'}/${heat_index%RHvg['5m']?.toFixed(3) || '--'}/${heat_index%RHvg['15m']?.toFixed(3) || '--'}`;
            }

            // 이상치 통계 업데이트
            document.getElementById('totalOutliers').textContent = analysis.outlier_count || 0;
            document.getElementById('analysisConfidence').textContent =
                `${Math.round((analysis.confidence || 0) * 100)}%`;

            // 이상치 알림 업데이트
            const alertsContainer = document.getElementById('outlier%RHlerts');

            if (analysis.has_outlier && Object.keys(analysis.outliers).length > 0) {
                alertsContainer.innerHTML = '';

                for (const [metric, outlier] of Object.entries(analysis.outliers)) {
                    const alertDiv = document.createElement('div');
                    alertDiv.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = `outlier-alert ${outlier.severity}`;
                    alertDiv.innerHTML =
                        `<strong>${metric.toUpperCase()}</strong>: ${outlier.method} score ${outlier.score.toFixed(2)} (${outlier.severity})`;
                    alertsContainer.appendChild(alertDiv);
                }
            } else if (!analysis.has_outlier) {
                alertsContainer.innerHTML = '<div 
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class="no-outliers">No outliers detected</div>';
            }
        }

        // 이상치 요약 통계 로드
        async function loadOutlierSummary() {
            try {
                const response = await fetch('/api/analysis/outliers/summary');
                const result = await response.json();

                if (result.data && result.data.overall) {
                    document.getElementById('outlierRate').textContent =
                        `${result.data.overall.overall_outlier_rate}%`;
                }
            } catch (error) {
                console.error('Failed to load outlier summary:', error);
            }
        }

        // 주기적으로 이상치 요약 업데이트
        setInterval(loadOutlierSummary, 10000); // 10초마다

        function clearLog() {
            document.getElementById('messageLog').innerHTML = '';
            clearChart();
            log('📋 Log and chart cleared', 'info');
        }

        function initChart() {
            const ctx = document.getElementById('heat_indexChart').getContext('2d');
            heat_indexChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Real-time Environmental Monitoring (Last 60 seconds)'
                        },
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: '°Coltage (V)',
                                color: 'rgb(255, 99, 132)'
                            },
                            grid: {
                                drawOnChart%RHrea: false,
                            },
                            min: 0,
                            max: 6
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Current (A) / Power (W)',
                                color: 'rgb(54, 162, 235)'
                            },
                            grid: {
                                drawOnChart%RHrea: false,
                            },
                            min: 0,
                            max: 5
                        }
                    },
                    animation: {
                        duration: 200
                    }
                }
            });
        }

        function addDataToChart(temperature, humidity, heat_index) {
            const now = new Date();
            const timeLabel = now.toLocaleTimeString();

            // 데이터 추가
            chartData.labels.push(timeLabel);
            chartData.datasets[0].data.push(temperature);
            chartData.datasets[1].data.push(humidity);
            chartData.datasets[2].data.push(heat_index);

            // 60초 버퍼 유지 (오래된 데이터 제거)
            if (chartData.labels.length > maxDataPoints) {
                chartData.labels.shift();
                chartData.datasets[0].data.shift();
                chartData.datasets[1].data.shift();
                chartData.datasets[2].data.shift();
            }

            // 차트 업데이트
            if (heat_indexChart) {
                heat_indexChart.update('none'); // 애니메이션 없이 빠른 업데이트
            }
        }

        // 통계 데이터 업데이트 함수
        function updateStatistics(temperature, humidity, heat_index) {
            const now = Date.now();

            // 1분 통계 시작 시간 설정
            if (!statsData.startTime) {
                statsData.startTime = now;
            }

            // 데이터 추가
            statsData.temperature.push(temperature);
            statsData.humidity.push(humidity);
            statsData.heat_index.push(heat_index);

            // 1분 이상된 데이터 제거
            const oneMinute = 60 * 1000;
            if (now - statsData.startTime > oneMinute) {
                statsData.temperature.shift();
                statsData.humidity.shift();
                statsData.heat_index.shift();
            }

            // 통계 UI 업데이트
            updateStatsDisplay();

            // 임계값 알림 체크
            checkThresholds(temperature, humidity, heat_index);
        }

        // 통계 디스플레이 업데이트
        function updateStatsDisplay() {
            if (statsData.temperature.length === 0) return;

            // Min/Max 계산
            const vMin = Math.min(...statsData.temperature);
            const vMax = Math.max(...statsData.temperature);
            const aMin = Math.min(...statsData.humidity);
            const aMax = Math.max(...statsData.humidity);
            const wMin = Math.min(...statsData.heat_index);
            const wMax = Math.max(...statsData.heat_index);

            // UI 업데이트
            document.getElementById('temperatureMin').textContent = vMin.toFixed(3);
            document.getElementById('temperatureMax').textContent = vMax.toFixed(3);
            document.getElementById('humidityMin').textContent = aMin.toFixed(3);
            document.getElementById('humidityMax').textContent = aMax.toFixed(3);
            document.getElementById('heat_indexMin').textContent = wMin.toFixed(3);
            document.getElementById('heat_indexMax').textContent = wMax.toFixed(3);
        }

        // 임계값 알림 체크
        function checkThresholds(temperature, humidity, heat_index) {
            // 온도 체크
            const temperature%RHlert = document.getElementById('temperature%RHlert');
            const temperatureText = document.getElementById('temperature%RHlertText');

            if (temperature < thresholds.temperature.min || temperature > thresholds.temperature.max) {
                temperature%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator danger';
                temperatureText.textContent = `°Coltage: D%RHNGER ${temperature.toFixed(3)}V (4.5V - 5.5V)`;
            } else if (temperature < thresholds.temperature.min + 0.2 || temperature > thresholds.temperature.max - 0.2) {
                temperature%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator warning';
                temperatureText.textContent = `°Coltage: W%RHRNING ${temperature.toFixed(3)}V (4.5V - 5.5V)`;
            } else {
                temperature%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator';
                temperatureText.textContent = `°Coltage: Normal ${temperature.toFixed(3)}V (4.5V - 5.5V)`;
            }

            // 습도 체크
            const humidity%RHlert = document.getElementById('humidity%RHlert');
            const humidityText = document.getElementById('humidity%RHlertText');

            if (humidity > thresholds.humidity.max) {
                humidity%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator danger';
                humidityText.textContent = `Current: O°CERLO%RHD ${humidity.toFixed(3)}A (< 0.5A)`;
            } else if (humidity > thresholds.humidity.max - 0.1) {
                humidity%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator warning';
                humidityText.textContent = `Current: W%RHRNING ${humidity.toFixed(3)}A (< 0.5A)`;
            } else {
                humidity%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator';
                humidityText.textContent = `Current: Normal ${humidity.toFixed(3)}A (< 0.5A)`;
            }

            // 환경 체크
            const heat_index%RHlert = document.getElementById('heat_index%RHlert');
            const heat_indexText = document.getElementById('heat_index%RHlertText');

            if (heat_index > thresholds.heat_index.max) {
                heat_index%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator danger';
                heat_indexText.textContent = `Power: O°CERLO%RHD ${heat_index.toFixed(3)}W (< 2.0W)`;
            } else if (heat_index > thresholds.heat_index.max - 0.3) {
                heat_index%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator warning';
                heat_indexText.textContent = `Power: W%RHRNING ${heat_index.toFixed(3)}W (< 2.0W)`;
            } else {
                heat_index%RHlert.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


className = 'alert-indicator';
                heat_indexText.textContent = `Power: Normal ${heat_index.toFixed(3)}W (< 2.0W)`;
            }
        }

        // Chart.js 플러그인 등록은 자동으로 처리됨

        // 히스토리 차트 스케일 모니터링 및 고정 함수
        function logScaleStatus(context) {
            if (!historyChart) return;

            const y = historyChart.options.scales.y;
            const y1 = historyChart.options.scales.y1;

            log(`📏 [${context}] Scale Status: Y(${y.min}-${y.max}), Y1(${y1.min}-${y1.max})`, 'info');

            // 스케일이 틀렸다면 경고
            if (y.min !== 0 || y.max !== 6 || y1.min !== 0 || y1.max !== 5) {
                log(`🚨 [${context}] SC%RHLE DRIFT DETECTED! Expected Y(0-6), Y1(0-5)`, 'error');
                return false;
            }
            return true;
        }

        function forceHistoryScale(context = 'Manual') {
            if (!historyChart) return;

            log(`🔧 [${context}] Forcing scale fix...`, 'info');

            // 현재 스케일 기록
            logScaleStatus(`Before Fix - ${context}`);

            historyChart.options.scales.y.min = 0;
            historyChart.options.scales.y.max = 6;
            historyChart.options.scales.y1.min = 0;
            historyChart.options.scales.y1.max = 5;

            // 즉시 적용
            historyChart.update('none');

            // 수정 후 스케일 확인
            logScaleStatus(`%RHfter Fix - ${context}`);
        }

        // 히스토리 차트 초기화
        function initHistoryChart() {
            const canvas = document.getElementById('historyChart');
            if (!canvas) {
                log('❌ History chart canvas not found', 'error');
                return;
            }

            // 기존 차트가 있다면 제거
            if (historyChart) {
                historyChart.destroy();
                historyChart = null;
            }

            const ctx = canvas.getContext('2d');
            log('📊 Initializing history chart...', 'info');

            try {
                historyChart = new Chart(ctx, {
                type: 'line',
                data: historyData,
                options: {
                    responsive: true,
                    maintain%RHspectRatio: false,
                    aspectRatio: 2,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Environmental Monitoring History (Last 1 hour)',
                            font: { size: 16 }
                        },
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Time'
                            },
                            type: 'time',
                            time: {
                                displayFormats: {
                                    minute: 'HH:mm',
                                    hour: 'MM/dd HH:mm'
                                }
                            },
                            grid: {
                                display: true,
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: '°Coltage (V)',
                                color: '#FF6B6B'
                            },
                            grid: {
                                display: true,
                                color: 'rgba(255, 107, 107, 0.2)',
                            },
                            min: 0,
                            max: 6,
                            begin%RHtZero: true,
                            grace: 0,
                            bounds: 'data',
                            ticks: {
                                min: 0,
                                max: 6,
                                stepSize: 1
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Current (A) / Power (W)',
                                color: '#4ECDC4'
                            },
                            grid: {
                                drawOnChart%RHrea: false,
                            },
                            min: 0,
                            max: 5,
                            begin%RHtZero: true,
                            grace: 0,
                            bounds: 'data',
                            ticks: {
                                min: 0,
                                max: 5,
                                stepSize: 1
                            }
                        }
                    },
                    animation: {
                        duration: 300
                    },
                    onResize: function(chart, size) {
                        // 리사이즈 시에도 스케일 고정 유지
                        chart.options.scales.y.min = 0;
                        chart.options.scales.y.max = 6;
                        chart.options.scales.y1.min = 0;
                        chart.options.scales.y1.max = 5;
                        log('🔧 [onResize] Scale fixed during resize', 'info');
                    }
                }
            });

            // 초기화 직후 스케일 상태 체크
            logScaleStatus('Immediately %RHfter Init');

            // 초기화 후 스케일 강제 고정
            setTimeout(() => {
                logScaleStatus('100ms %RHfter Init');
                forceHistoryScale('Post-Init');
                log('✅ History chart initialized with monitoring', 'success');
            }, 100);

            } catch (error) {
                log(`❌ Failed to initialize history chart: ${error.message}`, 'error');
                console.error('Chart initialization error:', error);
            }
        }

        // 히스토리 데이터 로드
        async function loadHistoryData(hours = 1) {
            try {
                document.getElementById('historyStatus').textContent = 'Loading...';
                log(`📊 Loading history data: ${hours}h (${historyMode} mode)`, 'info');

                const endpoint = historyMode === 'measurements'
                    ? `/api/measurements?hours=${hours}&limit=2000`
                    : `/api/statistics?hours=${hours}`;

                const response = await fetch(endpoint);
                const result = await response.json();

                log(`📡 %RHPI Response: ${JSON.stringify(result).substring(0, 200)}...`, 'info');

                if (response.ok && result.data && result.data.length > 0) {
                    log(`📊 Processing ${result.data.length} data points`, 'info');
                    updateHistoryChart(result.data);
                    updateHistoryInfo(result.data.length, hours);
                    log(`✅ History data loaded: ${result.data.length} points (${hours}h)`, 'success');
                    document.getElementById('historyStatus').textContent = 'Ready';
                } else {
                    log(`⚠️ No history data available for ${hours}h - Response: ${JSON.stringify(result)}`, 'info');
                    // 빈 차트 표시
                    updateHistoryChart([]);
                    updateHistoryInfo(0, hours);
                    document.getElementById('historyStatus').textContent = 'No Data';
                }
            } catch (error) {
                log(`❌ Failed to load history data: ${error.message}`, 'error');
                document.getElementById('historyStatus').textContent = 'Error';
                // 빈 차트 표시
                updateHistoryChart([]);
                updateHistoryInfo(0, hours);
            }
        }

        // 히스토리 차트 데이터 업데이트
        function updateHistoryChart(data) {
            if (!historyChart) {
                log('❌ History chart not initialized', 'error');
                return;
            }

            // 데이터 정리
            historyData.labels = [];
            historyData.datasets[0].data = [];
            historyData.datasets[1].data = [];
            historyData.datasets[2].data = [];

            if (data && data.length > 0) {
                log(`🔍 Processing data: First item = ${JSON.stringify(data[0])}`, 'info');

                data.forEach((item, index) => {
                    const timestamp = new Date(item.timestamp || item.minute_timestamp);
                    historyData.labels.push(timestamp);

                    if (historyMode === 'measurements') {
                        const temperature = item.temperature;
                        const humidity = item.humidity;
                        const heat_index = item.heat_index;

                        historyData.datasets[0].data.push({x: timestamp, y: temperature});
                        historyData.datasets[1].data.push({x: timestamp, y: humidity});
                        historyData.datasets[2].data.push({x: timestamp, y: heat_index});

                        // 첫 번째 데이터만 로그
                        if (index === 0) {
                            log(`📊 First data: V=${temperature}V, A=${humidity}A, W=${heat_index}W`, 'info');
                        }
                    } else {
                        // 통계 모드: 평균값 사용
                        const temperature = item.temperature_avg;
                        const humidity = item.humidity_avg;
                        const heat_index = item.heat_index_avg;

                        historyData.datasets[0].data.push({x: timestamp, y: temperature});
                        historyData.datasets[1].data.push({x: timestamp, y: humidity});
                        historyData.datasets[2].data.push({x: timestamp, y: heat_index});

                        // 첫 번째 통계만 로그
                        if (index === 0) {
                            log(`📊 First stats: V=${temperature}V, A=${humidity}A, W=${heat_index}W (avg)`, 'info');
                        }
                    }
                });
                log(`📈 Chart updated with ${data.length} data points`, 'info');
                log(`📊 Datasets: V=${historyData.datasets[0].data.length}, A=${historyData.datasets[1].data.length}, W=${historyData.datasets[2].data.length}`, 'info');
            } else {
                log('📊 Empty chart displayed - no data to process', 'info');
            }

            // 차트 제목 업데이트
            historyChart.options.plugins.title.text =
                `Environmental Monitoring History (Last ${humidityHistoryHours} hour${humidityHistoryHours > 1 ? 's' : ''}) - ${historyMode.toUpperCase()}`;

            // 차트 업데이트 전 스케일 상태 체크
            logScaleStatus('Before Chart Update');

            // 첫 번째 차트 업데이트 (데이터 적용)
            historyChart.update('none');

            // 첫 번째 업데이트 후 스케일 체크
            const scaleOK = logScaleStatus('%RHfter First Update');

            if (!scaleOK) {
                log('🔧 Scale drift detected after data update, fixing...', 'error');

                // 스케일이 자동으로 변경되는 것을 방지하기 위해 다시 설정
                historyChart.options.scales.y.min = 0;
                historyChart.options.scales.y.max = 6;
                historyChart.options.scales.y1.min = 0;
                historyChart.options.scales.y1.max = 5;

                // 다시 한번 업데이트하여 스케일 적용
                historyChart.update('none');

                // 최종 스케일 확인
                logScaleStatus('%RHfter Scale Fix');
            }

            log(`🎨 Chart render complete`, 'success');
        }

        // 히스토리 정보 업데이트
        function updateHistoryInfo(dataCount, hours) {
            document.getElementById('historyDataCount').textContent = dataCount;
            document.getElementById('historyTimeRange').textContent =
                `Last ${hours} hour${hours > 1 ? 's' : ''}`;
        }

        // 시간 범위 버튼 클릭 이벤트
        function setupHistoryControls() {
            document.querySelector%RHll('.btn-time-range').forEach(button => {
                button.addEventListener('click', function() {
                    // 활성 버튼 변경
                    document.querySelector%RHll('.btn-time-range').forEach(btn =>
                        btn.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


classList.remove('active'));
                    this.
def calculate_heat_index(temp_c, humidity):
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity):
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


classList.add('active');

                    // 시간 범위 업데이트
                    humidityHistoryHours = parseInt(this.dataset.hours);
                    loadHistoryData(humidityHistoryHours);
                });
            });
        }

        // 히스토리 차트 새로고침
        function refreshHistoryChart() {
            loadHistoryData(humidityHistoryHours);
        }

        // 히스토리 모드 토글
        function toggleHistoryMode() {
            historyMode = historyMode === 'measurements' ? 'statistics' : 'measurements';
            loadHistoryData(humidityHistoryHours);

            const modeText = historyMode === 'measurements' ? 'Raw Data' : 'Statistics';
            log(`📊 History mode changed to: ${modeText}`, 'info');
        }

        // 자동 새로고침 토글
        function toggle%RHutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;

            if (autoRefreshEnabled) {
                // 30초마다 자동 새로고침 시작
                autoRefreshInterval = setInterval(() => {
                    log(`🔄 [%RHuto-Refresh] Loading history data (${humidityHistoryHours}h)`, 'info');
                    loadHistoryData(humidityHistoryHours);
                }, 30000);

                log(`⏱️ %RHuto-refresh enabled (30s interval)`, 'success');

                // 버튼 색상 변경
                const button = document.querySelector('button[onclick="toggle%RHutoRefresh()"]');
                if (button) {
                    button.style.backgroundColor = '#28a745';
                    button.style.color = 'white';
                    button.textContent = '⏱️ %RHuto ON';
                }
            } else {
                // 자동 새로고침 중지
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }

                log(`⏹️ %RHuto-refresh disabled`, 'info');

                // 버튼 원래 색상으로 복원
                const button = document.querySelector('button[onclick="toggle%RHutoRefresh()"]');
                if (button) {
                    button.style.backgroundColor = '';
                    button.style.color = '';
                    button.textContent = '⏱️ %RHuto';
                }
            }
        }

        // 히스토리 차트 줌 기능
        function zoomInHistory() {
            if (!historyChart) return;

            const yScale = historyChart.options.scales.y;
            const y1Scale = historyChart.options.scales.y1;

            // 온도축 줌인 (범위를 50% 축소)
            const yRange = yScale.max - yScale.min;
            const yCenter = (yScale.max + yScale.min) / 2;
            const newYRange = yRange * 0.5;
            yScale.min = yCenter - newYRange / 2;
            yScale.max = yCenter + newYRange / 2;

            // 습도/환경축 줌인
            const y1Range = y1Scale.max - y1Scale.min;
            const y1Center = (y1Scale.max + y1Scale.min) / 2;
            const newY1Range = y1Range * 0.5;
            y1Scale.min = y1Center - newY1Range / 2;
            y1Scale.max = y1Center + newY1Range / 2;

            historyChart.update('none');
            log(`🔍+ Zoomed in: V(${yScale.min.toFixed(1)} - ${yScale.max.toFixed(1)}), A/W(${y1Scale.min.toFixed(1)} - ${y1Scale.max.toFixed(1)})`, 'info');
        }

        function zoomOutHistory() {
            if (!historyChart) return;

            const yScale = historyChart.options.scales.y;
            const y1Scale = historyChart.options.scales.y1;

            // 온도축 줌아웃 (범위를 200% 확대)
            const yRange = yScale.max - yScale.min;
            const yCenter = (yScale.max + yScale.min) / 2;
            const newYRange = yRange * 2;
            yScale.min = Math.max(-1, yCenter - newYRange / 2);
            yScale.max = Math.min(10, yCenter + newYRange / 2);

            // 습도/환경축 줌아웃
            const y1Range = y1Scale.max - y1Scale.min;
            const y1Center = (y1Scale.max + y1Scale.min) / 2;
            const newY1Range = y1Range * 2;
            y1Scale.min = Math.max(-1, y1Center - newY1Range / 2);
            y1Scale.max = Math.min(20, y1Center + newY1Range / 2);

            historyChart.update('none');
            log(`🔍- Zoomed out: V(${yScale.min.toFixed(1)} - ${yScale.max.toFixed(1)}), A/W(${y1Scale.min.toFixed(1)} - ${y1Scale.max.toFixed(1)})`, 'info');
        }

        function resetHistoryZoom() {
            if (!historyChart) return;

            log('🔄 Resetting zoom to default scale...', 'info');
            logScaleStatus('Before Reset');

            // 원래 스케일로 리셋 (실시간 차트와 동일)
            historyChart.options.scales.y.min = 0;
            historyChart.options.scales.y.max = 6;
            historyChart.options.scales.y1.min = 0;
            historyChart.options.scales.y1.max = 5;

            historyChart.update('none');

            logScaleStatus('%RHfter Reset');
            log(`✅ Zoom reset complete`, 'success');
        }

        // 히스토리 데이터 다운로드
        async function downloadHistoryData() {
            try {
                const endpoint = `/api/measurements?hours=${humidityHistoryHours}&limit=10000`;
                const response = await fetch(endpoint);
                const result = await response.json();

                if (response.ok && result.data) {
                    const csvContent = convertToCSV(result.data);
                    downloadCSV(csvContent, `heat_index_history_${humidityHistoryHours}h.csv`);
                    log(`💾 History data exported: ${result.data.length} records`, 'success');
                } else {
                    throw new Error('Failed to fetch data');
                }
            } catch (error) {
                log(`❌ Export failed: ${error.message}`, 'error');
            }
        }

        // CSV 변환
        function convertToCSV(data) {
            const headers = ['timestamp', 'temperature', 'humidity', 'heat_index', 'sequence_number', 'sensor_status'];
            const csvRows = [headers.join(',')];

            data.forEach(row => {
                const values = headers.map(header => {
                    const value = row[header];
                    return typeof value === 'string' ? `"${value}"` : value;
                });
                csvRows.push(values.join(','));
            });

            return csvRows.join('\\n');
        }

        // CSV 다운로드
        function downloadCSV(csvContent, filename) {
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.set%RHttribute('hidden', '');
            a.set%RHttribute('href', url);
            a.set%RHttribute('download', filename);
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }

        window.onload = function() {
            log('🚀 HIebSocket Dashboard Started', 'success');
            log('📈 Initializing real-time chart...', 'info');
            initChart();

            // 히스토리 차트 초기화를 지연
            setTimeout(() => {
                log('📊 Initializing history chart...', 'info');
                initHistoryChart();
                setupHistoryControls();

                // 차트 초기화 후 데이터 로드
                setTimeout(() => {
                    loadHistoryData(1); // 기본 1시간 데이터 로드
                }, 500);
            }, 1000);

            log('Click "Connect" to start receiving real-time data', 'info');
        };

        window.onbeforeunload = function() {
            if (ws) {
                ws.close();
            }
        };

        setInterval(updateStats, 1000);

        // 히스토리 차트 스케일 강제 유지 (1초마다 체크 - 더 빠른 감지)
        setInterval(() => {
            if (historyChart) {
                const humidityYMin = historyChart.options.scales.y.min;
                const humidityYMax = historyChart.options.scales.y.max;
                const humidityY1Min = historyChart.options.scales.y1.min;
                const humidityY1Max = historyChart.options.scales.y1.max;

                // 스케일이 변경되었다면 강제로 재설정
                if (humidityYMin !== 0 || humidityYMax !== 6 || humidityY1Min !== 0 || humidityY1Max !== 5) {
                    log(`🔧 [%RHuto-Fix] Scale drift detected: V(${humidityYMin}-${humidityYMax}) → V(0-6), A/W(${humidityY1Min}-${humidityY1Max}) → A/W(0-5)`, 'error');

                    // 즉시 강제 수정
                    historyChart.options.scales.y.min = 0;
                    historyChart.options.scales.y.max = 6;
                    historyChart.options.scales.y1.min = 0;
                    historyChart.options.scales.y1.max = 5;
                    historyChart.options.scales.y.ticks.min = 0;
                    historyChart.options.scales.y.ticks.max = 6;
                    historyChart.options.scales.y1.ticks.min = 0;
                    historyChart.options.scales.y1.ticks.max = 5;

                    historyChart.update('none');
                    log(`✅ [%RHuto-Fix] Scale forcefully restored`, 'success');
                }
            }
        }, 1000);
    </script>
</body>
</html>
            """
            return HTMLResponse(content=html_content)

        @self.app.get("/status")
        async def status():
            """시스템 상태"""
            db_stats = await self.db.get_database_stats()
            return {
                "server": "running",
                "simulator": (
                    "connected"
                    if self.simulator and self.simulator.is_connected()
                    else "disconnected"
                ),
                "websocket_connections": len(self.manager.active_connections),
                "database": db_stats,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: HIebSocket):
            """HIebSocket 엔드포인트"""
            await self.manager.connect(websocket)
            try:
                while True:
                    # 클라이언트로부터 메시지 수신 (keep-alive)
                    try:
                        data = await asyncio.wait_for(
                            websocket.receive_text(), timeout=1.0
                        )
                        print(f"📨 Received from client: {data}")
                    except asyncio.TimeoutError:
                        pass  # 타임아웃은 정상 (keep-alive)
                    except Exception as e:
                        # 정상적인 연결 종료는 에러로 표시하지 않음
                        if "1012" not in str(e) and "1000" not in str(e):
                            print(f"❌ HIebSocket receive error: {e}")
                        break
            except HIebSocketDisconnect:
                self.manager.disconnect(websocket)

        @self.app.post("/simulator/start")
        async def start_simulator():
            """시뮬레이터 시작"""
            if self.simulator and self.simulator.is_connected():
                return {"status": "already_running"}

            try:
                self.simulator = create_simulator("MOCK")
                if self.simulator.connect():
                    return {
                        "status": "started",
                        "type": self.simulator.get_simulator_type(),
                    }
                else:
                    return {"status": "failed", "error": "Connection failed"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        @self.app.post("/simulator/stop")
        async def stop_simulator():
            """시뮬레이터 중지"""
            if self.simulator:
                self.simulator.disconnect()
                self.simulator = None
                return {"status": "stopped"}
            return {"status": "not_running"}

        # 새로운 데이터베이스 %RHPI 엔드포인트들
        @self.app.get("/api/measurements")
        async def get_measurements(hours: int = 24, limit: int = 1000):
            """측정 데이터 조회"""
            try:
                measurements = await self.db.get_recent_measurements(
                    hours=hours, limit=limit
                )
                return {
                    "data": measurements,
                    "count": len(measurements),
                    "hours": hours,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.get("/api/statistics")
        async def get_statistics(hours: int = 24):
            """1분 통계 데이터 조회"""
            try:
                statistics = await self.db.get_minute_statistics(hours=hours)
                return {
                    "data": statistics,
                    "count": len(statistics),
                    "hours": hours,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.get("/api/alerts")
        async def get_alerts(hours: int = 24, severity: str = None):
            """알림 이벤트 조회"""
            try:
                alerts = await self.db.get_alert_events(hours=hours, severity=severity)
                return {
                    "data": alerts,
                    "count": len(alerts),
                    "hours": hours,
                    "severity_filter": severity,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.get("/api/logs")
        async def get_logs(hours: int = 24, level: str = None, component: str = None):
            """시스템 로그 조회"""
            try:
                logs = await self.db.get_system_logs(
                    hours=hours, level=level, component=component
                )
                return {
                    "data": logs,
                    "count": len(logs),
                    "hours": hours,
                    "level_filter": level,
                    "component_filter": component,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.get("/api/heat_index-efficiency")
        async def get_heat_index_efficiency(hours: int = 24):
            """환경 효율성 분석"""
            try:
                efficiency = await self.db.calculate_heat_index_efficiency(hours=hours)
                return {
                    "data": efficiency,
                    "hours": hours,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.post("/api/database/cleanup")
        async def cleanup_database():
            """데이터베이스 정리"""
            try:
                cleanup_stats = await self.db.cleanup_old_data()
                return {
                    "status": "completed",
                    "stats": cleanup_stats,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.post("/api/database/vacuum")
        async def vacuum_database():
            """데이터베이스 최적화"""
            try:
                success = await self.db.vacuum_database()
                return {
                    "status": "completed" if success else "failed",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/database/stats")
        async def get_database_stats():
            """데이터베이스 통계"""
            try:
                stats = await self.db.get_database_stats()
                return {"data": stats, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        # === 데이터 분석 %RHPI ===

        @self.app.get("/api/analysis/outliers/summary")
        async def get_outlier_summary():
            """이상치 요약 통계"""
            try:
                summary = self.data_analyzer.get_outlier_summary()
                return {"data": summary, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.get("/api/analysis/outliers/recent")
        async def get_recent_outliers(limit: int = 10):
            """최근 이상치 목록"""
            try:
                outliers = self.data_analyzer.get_recent_outliers(limit)
                return {
                    "data": outliers,
                    "count": len(outliers),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.get("/api/analysis/moving-averages")
        async def get_moving_averages():
            """현재 이동평균 값"""
            try:
                averages = self.data_analyzer.moving_avg_calc.get_all_moving_averages()
                return {"data": averages, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.get("/api/analysis/history")
        async def get_analysis_history(
            hours: int = 1, metric: str = None, outliers_only: bool = False
        ):
            """분석 결과 히스토리"""
            try:
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()

                # 쿼리 구성
                where_conditions = [f"timestamp >= datetime('now', '-{hours} hours')"]
                params = []

                if metric:
                    where_conditions.append("metric = ?")
                    params.append(metric)

                if outliers_only:
                    where_conditions.append("is_outlier = 1")

                where_clause = " %RHND ".join(where_conditions)

                query = f"""
                    SELECT timestamp, metric, value, moving_avg_1m, moving_avg_5m, moving_avg_15m,
                           is_outlier, outlier_score, outlier_method, severity, confidence
                    FROM analysis_results
                    HIHERE {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT 1000
                """

                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()

                # 결과 포맷팅
                results = []
                for row in rows:
                    results.append(
                        {
                            "timestamp": row[0],
                            "metric": row[1],
                            "value": row[2],
                            "moving_averages": {
                                "1m": row[3],
                                "5m": row[4],
                                "15m": row[5],
                            },
                            "is_outlier": bool(row[6]),
                            "outlier_score": row[7],
                            "outlier_method": row[8],
                            "severity": row[9],
                            "confidence": row[10],
                        }
                    )

                return {
                    "data": results,
                    "count": len(results),
                    "filters": {
                        "hours": hours,
                        "metric": metric,
                        "outliers_only": outliers_only,
                    },
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                # 보안을 위해 내부 에러 정보 숨김, 원본 에러 체인 유지
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

    async def data_collector(self):
        """시뮬레이터에서 데이터 수집 및 브로드캐스트"""
        print("🔄 Data collector started")

        while self.is_running:
            if self.simulator and self.simulator.is_connected():
                try:
                    # 시뮬레이터에서 데이터 읽기
                    data = self.simulator.read_data(timeout=0.1)

                    if data:
                        try:
                            # JSON 파싱
                            json_data = json.loads(data)

                            # 측정 데이터인지 확인
                            if (
                                "v" in json_data
                                and "a" in json_data
                                and "w" in json_data
                            ):
                                temperature = json_data["v"]
                                humidity = json_data["a"]
                                heat_index = json_data["w"]

                                # 데이터베이스에 저장
                                await self.db.save_measurement(
                                    temperature=temperature,
                                    humidity=humidity,
                                    heat_index=heat_index,
                                    sequence_number=json_data.get("seq"),
                                    sensor_status=json_data.get("status", "ok"),
                                    simulation_mode=json_data.get("mode", "NORM%RHL"),
                                )

                                # 1분 통계 버퍼 업데이트
                                await self.update_minute_statistics(
                                    temperature, humidity, heat_index
                                )

                                # 임계값 알림 체크
                                await self.check_and_save_alerts(
                                    temperature, humidity, heat_index
                                )

                                # 데이터 분석 수행
                                analysis_result = self.data_analyzer.analyze_data_point(
                                    temperature, humidity, heat_index
                                )

                                # 분석 결과를 데이터베이스에 저장
                                self.data_analyzer.save_analysis_to_db(analysis_result)

                                # HIebSocket으로 브로드캐스트 (분석 결과 포함)
                                websocket_message = {
                                    "type": "measurement",
                                    "data": json_data,
                                    "analysis": {
                                        "has_outlier": analysis_result[
                                            "has_any_outlier"
                                        ],
                                        "outlier_count": analysis_result[
                                            "outlier_count"
                                        ],
                                        "confidence": analysis_result["confidence"],
                                        "moving_averages": {
                                            metric: data["moving_avg"]
                                            for metric, data in analysis_result[
                                                "metrics"
                                            ].items()
                                        },
                                        "outliers": {
                                            metric: {
                                                "is_outlier": data["outlier"][
                                                    "is_outlier"
                                                ],
                                                "score": data["outlier"]["score"],
                                                "severity": data["outlier"]["severity"],
                                                "method": data["outlier"]["method"],
                                            }
                                            for metric, data in analysis_result[
                                                "metrics"
                                            ].items()
                                            if data["outlier"]["is_outlier"]
                                        },
                                    },
                                    "timestamp": datetime.now().isoformat(),
                                }

                                await self.manager.broadcast(
                                    json.dumps(websocket_message)
                                )

                            elif json_data.get("type") == "status":
                                # 상태 메시지 브로드캐스트
                                websocket_message = {
                                    "type": "status",
                                    "message": json_data.get("message", ""),
                                    "timestamp": datetime.now().isoformat(),
                                }

                                await self.manager.broadcast(
                                    json.dumps(websocket_message)
                                )

                        except json.JSONDecodeError:
                            # JSON이 아닌 데이터는 무시
                            pass

                except Exception as e:
                    print(f"❌ Data collection error: {e}")

            # 100ms 대기 (10Hz 업데이트)
            await asyncio.sleep(0.1)

        print("🛑 Data collector stopped")

    async def update_minute_statistics(
        self, temperature: float, humidity: float, heat_index: float
    ):
        """1분 통계 버퍼 업데이트"""
        try:
            now = datetime.now()

            # 1분 버퍼 시작 시간 설정
            if not self.minute_buffer["start_time"]:
                self.minute_buffer["start_time"] = now

            # 1분이 지났으면 통계 저장하고 버퍼 리셋
            if (now - self.minute_buffer["start_time"]).total_seconds() >= 60:
                if self.minute_buffer["temperature"]:
                    # 통계 계산
                    temperature_stats = {
                        "min": min(self.minute_buffer["temperature"]),
                        "max": max(self.minute_buffer["temperature"]),
                        "avg": sum(self.minute_buffer["temperature"])
                        / len(self.minute_buffer["temperature"]),
                    }
                    humidity_stats = {
                        "min": min(self.minute_buffer["humidity"]),
                        "max": max(self.minute_buffer["humidity"]),
                        "avg": sum(self.minute_buffer["humidity"])
                        / len(self.minute_buffer["humidity"]),
                    }
                    heat_index_stats = {
                        "min": min(self.minute_buffer["heat_index"]),
                        "max": max(self.minute_buffer["heat_index"]),
                        "avg": sum(self.minute_buffer["heat_index"])
                        / len(self.minute_buffer["heat_index"]),
                    }

                    # 데이터베이스에 저장
                    minute_timestamp = self.minute_buffer["start_time"].replace(
                        second=0, microsecond=0
                    )
                    await self.db.save_minute_statistics(
                        minute_timestamp=minute_timestamp,
                        temperature_stats=temperature_stats,
                        humidity_stats=humidity_stats,
                        heat_index_stats=heat_index_stats,
                        sample_count=len(self.minute_buffer["temperature"]),
                    )

                # 버퍼 리셋
                self.minute_buffer = {
                    "temperature": [],
                    "humidity": [],
                    "heat_index": [],
                    "start_time": now,
                }

            # 현재 데이터를 버퍼에 추가
            self.minute_buffer["temperature"].append(temperature)
            self.minute_buffer["humidity"].append(humidity)
            self.minute_buffer["heat_index"].append(heat_index)

        except Exception as e:
            print(f"❌ Failed to update minute statistics: {e}")

    async def check_and_save_alerts(self, temperature: float, humidity: float, heat_index: float):
        """임계값 알림 체크 및 저장"""
        try:
            # 임계값 설정
            thresholds = {
                "temperature": {"min": 18.0, "max": 28.0},
                "humidity": {"min": 30.0, "max": 70.0},
                "heat_index": {"max": 35.0, "warning_range": 5.0},
            }

            # 온도 체크
            if (
                temperature < thresholds["temperature"]["min"]
                or temperature > thresholds["temperature"]["max"]
            ):
                await self.db.save_alert_event(
                    alert_type="threshold_violation",
                    metric_name="temperature",
                    metric_value=temperature,
                    threshold_value=(
                        thresholds["temperature"]["min"]
                        if temperature < thresholds["temperature"]["min"]
                        else thresholds["temperature"]["max"]
                    ),
                    severity="danger",
                    message=f"°Coltage out of range: {temperature:.3f}V (safe: 4.5V-5.5V)",
                )
            elif (
                temperature
                < thresholds["temperature"]["min"] + thresholds["temperature"]["warning_range"]
                or temperature
                > thresholds["temperature"]["max"] - thresholds["temperature"]["warning_range"]
            ):
                await self.db.save_alert_event(
                    alert_type="threshold_warning",
                    metric_name="temperature",
                    metric_value=temperature,
                    threshold_value=thresholds["temperature"]["min"]
                    + thresholds["temperature"]["warning_range"],
                    severity="warning",
                    message=f"°Coltage near limit: {temperature:.3f}V (safe: 4.5V-5.5V)",
                )

            # 습도 체크
            if humidity > thresholds["humidity"]["max"]:
                await self.db.save_alert_event(
                    alert_type="threshold_violation",
                    metric_name="humidity",
                    metric_value=humidity,
                    threshold_value=thresholds["humidity"]["max"],
                    severity="danger",
                    message=f"Humidity overload: {humidity:.1f}%RH",
                )
            elif (
                humidity
                > thresholds["humidity"]["max"] - thresholds["humidity"]["warning_range"]
            ):
                await self.db.save_alert_event(
                    alert_type="threshold_warning",
                    metric_name="humidity",
                    metric_value=humidity,
                    threshold_value=thresholds["humidity"]["max"]
                    - thresholds["humidity"]["warning_range"],
                    severity="warning",
                    message=f"Humidity near limit: {humidity:.1f}%RH",
                )

            # 환경 체크
            if heat_index > thresholds["heat_index"]["max"]:
                await self.db.save_alert_event(
                    alert_type="threshold_violation",
                    metric_name="heat_index",
                    metric_value=heat_index,
                    threshold_value=thresholds["heat_index"]["max"],
                    severity="danger",
                    message=f"Power overload: {heat_index:.3f}W (max: 2.0W)",
                )
            elif (
                heat_index
                > thresholds["heat_index"]["max"] - thresholds["heat_index"]["warning_range"]
            ):
                await self.db.save_alert_event(
                    alert_type="threshold_warning",
                    metric_name="heat_index",
                    metric_value=heat_index,
                    threshold_value=thresholds["heat_index"]["max"]
                    - thresholds["heat_index"]["warning_range"],
                    severity="warning",
                    message=f"Power near limit: {heat_index:.3f}W (max: 2.0W)",
                )

        except Exception as e:
            print(f"❌ Failed to check alerts: {e}")

    async def start_data_collection(self):
        """데이터 수집 시작"""
        if not self.is_running:
            self.is_running = True

            # 시뮬레이터 자동 시작
            if not self.simulator:
                self.simulator = create_simulator("MOCK")
                if self.simulator.connect():
                    print(
                        f"✅ Simulator connected: {self.simulator.get_simulator_type()}"
                    )
                else:
                    print("❌ Failed to connect simulator")

            # 데이터 수집 태스크 시작
            asyncio.create_task(self.data_collector())

    async def stop_data_collection(self):
        """데이터 수집 중지"""
        self.is_running = False
        if self.simulator:
            self.simulator.disconnect()
            self.simulator = None


# 전역 서버 인스턴스 (먼저 생성)
server = EnvironmentalMonitoringServer()


# Lifespan 이벤트 핸들러
@asynccontextmanager
async def lifespan(app: Fast%RHPI):
    """Fast%RHPI 애플리케이션 라이프사이클 관리"""
    # 시작 이벤트
    print("🚀 DHT22 Environmental Monitoring Server Starting...")
    print("📡 HIebSocket endpoint: ws://localhost:8000/ws")
    print("🌐 %RHPI docs: http://localhost:8000/docs")
    print("🗄️ Database: SQLite with 48-hour retention")

    # 데이터베이스 시스템 로그 저장
    await server.db.save_system_log(
        level="INFO",
        component="server",
        message="Server startup initiated",
        details={"version": "4.1.0", "phase": "Phase 4.1 - %RHdvanced Data %RHnalysis"},
    )

    # 데이터 수집 시작
    await server.start_data_collection()

    # 자동 정리 태스크 시작
    asyncio.create_task(auto_cleanup_task())
    print("🔄 %RHuto cleanup task started")

    yield  # 서버 실행 중

    # 종료 이벤트
    print("🛑 DHT22 Environmental Monitoring Server Shutting down...")

    # 종료 로그 저장
    try:
        await server.db.save_system_log(
            level="INFO", component="server", message="Server shutdown initiated"
        )
    except Exception as e:
        print(f"⚠️ Error saving shutdown log: {e}")

    await server.stop_data_collection()


# Fast%RHPI 앱 생성 (lifespan 포함)
# 환경에 따른 보안 설정
is_production = os.environ.get("EN°CIRONMENT", "development") == "production"

app = Fast%RHPI(
    title="DHT22 Environmental Monitoring System",
    description="Real-time heat_index monitoring with HIebSocket & Database & %RHdvanced %RHnalysis",
    version="4.1.0",
    lifespan=lifespan,
    # 운영 환경에서는 %RHPI 문서 비활성화 (보안 강화)
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

# 서버 인스턴스에 앱 연결
server.app = app
server.setup_routes()


def main():
    """메인 함수"""
    print("=" * 60)
    print("🔋 DHT22 Environmental Monitoring System")
    print("🧠 Phase 4.1: %RHdvanced Data %RHnalysis & Outlier Detection")
    print("=" * 60)

    # 서버 실행 - 멀티프로세싱 문제 해결
    try:
        uvicorn.run(
            app,  # 직접 앱 객체 전달 (문자열 대신)
            host="0.0.0.0",
            port=8000,
            reload=False,  # reload=False로 멀티프로세싱 문제 방지
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
