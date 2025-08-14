# DHT22 지능형 온습도 모니터링 시스템 설계서

## 📋 프로젝트 개요

### 🎯 목표
Arduino UNO R4 WiFi와 DHT22 센서를 활용하여 온도와 습도를 실시간으로 측정하고, 고급 데이터 분석(이동평균, 이상치 탐지)을 수행하며, 웹 대시보드를 통해 시각화하는 **산업용 수준의 지능형 온습도 모니터링 시스템** 구축

### 🌟 주요 기능
- **🤖 Arduino DHT22 시뮬레이터**: 실제 하드웨어 없이도 다양한 환경 조건(정상, 고온, 저온, 고습, 저습 등)을 시뮬레이션
- **📊 실시간 모니터링 대시보드**: Chart.js 기반의 멀티라인 실시간 그래프(온도, 습도, 체감온도)
- **💾 48시간 데이터 저장 및 분석**: SQLite를 사용한 시계열 데이터 저장 및 히스토리 차트
- **🧠 지능형 데이터 분석**: 이동평균 및 Z-score & IQR 듀얼 이상치 탐지
- **🚨 스마트 알림 시스템**: 온도/습도 임계값 기반 알림 및 불쾌지수 계산
- **🐳 Docker 지원**: 멀티스테이지 빌드를 통한 효율적인 배포

## 🏗️ 시스템 아키텍처

### 📊 전체 시스템 구조
```
┌─────────────────────────────────────────────────────────────────┐
│                    DHT22 모니터링 시스템                          │
├─────────────────────────────────────────────────────────────────┤
│  Hardware Layer                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Arduino UNO R4  │    │   DHT22 센서    │                    │
│  │     WiFi        │◄───┤  온도/습도 측정  │                    │
│  └─────────────────┘    └─────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│  Communication Layer                                            │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Serial/WiFi   │    │  JSON Protocol  │                    │
│  │  Communication  │◄───┤   Data Format   │                    │
│  └─────────────────┘    └─────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│  Backend Layer (Python FastAPI)                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Data Capture  │    │  Data Analysis  │    │  Database   │ │
│  │   & Validation  │◄───┤   & Processing  │◄───┤  Manager    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                       │                     │      │
│           ▼                       ▼                     ▼      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   WebSocket     │    │  Alert System   │    │   SQLite    │ │
│  │   Real-time     │    │   & Threshold   │    │  48h Data   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer (Web Dashboard)                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  Real-time      │    │   History       │    │   Analysis  │ │
│  │  Dashboard      │    │   Charts        │    │   Panel     │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 🔧 기술 스택

#### Hardware
- **Arduino UNO R4 WiFi**
- **DHT22 온습도 센서**
- **10kΩ 풀업 저항**

#### Backend
- **Python 3.9+**
- **FastAPI 0.116.1** - 고성능 웹 프레임워크
- **Uvicorn** - ASGI 서버
- **WebSocket** - 실시간 통신
- **SQLite** - 경량 데이터베이스
- **NumPy** - 수치 계산
- **pySerial** - 시리얼 통신

#### Frontend
- **Chart.js 4.4.4** - 실시간 차트
- **HTML5/CSS3/JavaScript** - 웹 인터페이스

#### DevOps
- **Docker & Docker Compose**
- **Ruff + Black** - 코드 품질 관리
- **Pytest** - 테스트 프레임워크

## 📊 데이터 모델

### 🌡️ 센서 데이터 구조
```json
{
  "timestamp": "2025-08-14T10:30:00Z",
  "temperature": 25.6,
  "humidity": 65.2,
  "heat_index": 26.8,
  "dew_point": 18.4,
  "sequence_number": 1234,
  "sensor_status": "ok",
  "simulation_mode": "NORMAL"
}
```

### 📈 분석 데이터 구조
```json
{
  "moving_averages": {
    "temperature": {
      "1min": 25.5,
      "5min": 25.3,
      "15min": 25.1
    },
    "humidity": {
      "1min": 65.0,
      "5min": 64.8,
      "15min": 64.5
    }
  },
  "outliers": {
    "total_count": 2,
    "outlier_rate": 0.8,
    "confidence": 95,
    "alerts": [
      {
        "metric": "temperature",
        "value": 35.2,
        "severity": "high",
        "method": "z_score"
      }
    ]
  }
}
```

## 🗄️ 데이터베이스 설계

### 📋 테이블 구조

#### 1. climate_measurements (기본 측정 데이터)
```sql
CREATE TABLE climate_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    heat_index REAL,
    dew_point REAL,
    sequence_number INTEGER,
    sensor_status TEXT,
    simulation_mode TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. minute_statistics (1분 통계)
```sql
CREATE TABLE minute_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    minute_timestamp DATETIME NOT NULL,
    temperature_min REAL NOT NULL,
    temperature_max REAL NOT NULL,
    temperature_avg REAL NOT NULL,
    humidity_min REAL NOT NULL,
    humidity_max REAL NOT NULL,
    humidity_avg REAL NOT NULL,
    heat_index_avg REAL,
    sample_count INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(minute_timestamp)
);
```

#### 3. alert_events (알림 이벤트)
```sql
CREATE TABLE alert_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    alert_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    threshold_value REAL NOT NULL,
    severity TEXT NOT NULL,
    message TEXT,
    resolved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🎮 시뮬레이션 모드

### 🔄 Arduino 시뮬레이터 모드
1. **NORMAL** - 정상 환경 (20-25°C, 40-60% 습도)
2. **HOT_DRY** - 고온 건조 (30-40°C, 20-40% 습도)
3. **COLD_WET** - 저온 다습 (5-15°C, 70-90% 습도)
4. **EXTREME_HOT** - 극고온 (40-50°C, 10-30% 습도)
5. **EXTREME_COLD** - 극저온 (-10-5°C, 60-80% 습도)
6. **FLUCTUATING** - 급격한 변화 (랜덤 변동)

### 📊 시뮬레이션 데이터 생성 로직
```cpp
// Arduino 시뮬레이터 예시
void generateSimulationData(String mode) {
    if (mode == "NORMAL") {
        temperature = 22.5 + random(-25, 25) / 10.0;
        humidity = 50.0 + random(-100, 100) / 10.0;
    } else if (mode == "HOT_DRY") {
        temperature = 35.0 + random(-50, 50) / 10.0;
        humidity = 30.0 + random(-100, 100) / 10.0;
    }
    // ... 다른 모드들
}
```

## 🧠 데이터 분석 엔진

### 📈 이동평균 계산
- **1분 이동평균**: 최근 60초 데이터
- **5분 이동평균**: 최근 300초 데이터
- **15분 이동평균**: 최근 900초 데이터

### 🚨 이상치 탐지 알고리즘

#### 1. Z-Score 방법
```python
def detect_outliers_zscore(data, threshold=2.5):
    mean = np.mean(data)
    std = np.std(data)
    z_scores = [(x - mean) / std for x in data]
    return [abs(z) > threshold for z in z_scores]
```

#### 2. IQR (Interquartile Range) 방법
```python
def detect_outliers_iqr(data, factor=1.5):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    return [(x < lower_bound or x > upper_bound) for x in data]
```

## 🚨 알림 시스템

### 📊 임계값 설정
```python
THRESHOLDS = {
    "temperature": {
        "min": 18.0,    # 최저 온도 (°C)
        "max": 28.0,    # 최고 온도 (°C)
        "critical_min": 10.0,  # 위험 최저 온도
        "critical_max": 35.0   # 위험 최고 온도
    },
    "humidity": {
        "min": 30.0,    # 최저 습도 (%)
        "max": 70.0,    # 최고 습도 (%)
        "critical_min": 20.0,  # 위험 최저 습도
        "critical_max": 80.0   # 위험 최고 습도
    },
    "heat_index": {
        "caution": 27.0,     # 주의 체감온도
        "extreme_caution": 32.0,  # 경고 체감온도
        "danger": 40.0       # 위험 체감온도
    }
}
```

### 🌡️ 체감온도 (Heat Index) 계산
```python
def calculate_heat_index(temperature, humidity):
    """
    체감온도 계산 (미국 기상청 공식)
    """
    if temperature < 27:
        return temperature
    
    T = temperature
    H = humidity
    
    HI = (-42.379 + 2.04901523*T + 10.14333127*H 
          - 0.22475541*T*H - 6.83783e-3*T*T 
          - 5.481717e-2*H*H + 1.22874e-3*T*T*H 
          + 8.5282e-4*T*H*H - 1.99e-6*T*T*H*H)
    
    return round(HI, 1)
```

## 🌐 웹 대시보드 설계

### 📊 대시보드 구성 요소

#### 1. 실시간 데이터 패널
- **온도 게이지**: 현재 온도 표시 (색상 코딩)
- **습도 게이지**: 현재 습도 표시 (색상 코딩)
- **체감온도**: Heat Index 계산값
- **이슬점**: Dew Point 계산값

#### 2. 실시간 차트
- **멀티라인 차트**: 온도, 습도, 체감온도 동시 표시
- **60초 버퍼**: 최근 1분간 데이터 실시간 업데이트
- **자동 스케일링**: Y축 자동 조정

#### 3. 1분 통계 패널
```html
<div class="stats-grid">
    <div class="stats-metric temperature">
        <div class="stats-title">🌡️ Temperature</div>
        <div class="stats-values">
            <div class="stats-value">
                <div class="stats-value-num" id="tempMin">--</div>
                <div class="stats-value-label">MIN (°C)</div>
            </div>
            <div class="stats-value">
                <div class="stats-value-num" id="tempMax">--</div>
                <div class="stats-value-label">MAX (°C)</div>
            </div>
        </div>
    </div>
    <!-- 습도 통계 패널 -->
</div>
```

#### 4. 히스토리 차트
- **시간 범위 선택**: 1H, 6H, 24H, 48H
- **줌/팬 기능**: Chart.js 플러그인 활용
- **데이터 내보내기**: CSV 다운로드
- **자동 새로고침**: 선택적 자동 업데이트

#### 5. 데이터 분석 패널
- **이동평균 표시**: 1분/5분/15분 평균값
- **이상치 탐지 결과**: 실시간 이상치 알림
- **신뢰도 지표**: 분석 결과 신뢰도

## 🔄 API 설계

### 📡 WebSocket 엔드포인트
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 실시간 데이터 브로드캐스트
            data = await get_latest_sensor_data()
            await manager.broadcast(json.dumps(data))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 🔍 REST API 엔드포인트

#### 1. 현재 데이터 조회
```python
@app.get("/api/current")
async def get_current_data():
    return {
        "temperature": 25.6,
        "humidity": 65.2,
        "heat_index": 26.8,
        "dew_point": 18.4,
        "timestamp": "2025-08-14T10:30:00Z"
    }
```

#### 2. 히스토리 데이터 조회
```python
@app.get("/api/history")
async def get_history_data(hours: int = 24):
    data = await db.get_recent_measurements(hours=hours)
    return {"data": data, "count": len(data)}
```

#### 3. 통계 데이터 조회
```python
@app.get("/api/statistics")
async def get_statistics(hours: int = 24):
    stats = await db.get_minute_statistics(hours=hours)
    return {"statistics": stats}
```

#### 4. 분석 결과 조회
```python
@app.get("/api/analysis")
async def get_analysis_data():
    analysis = await analyzer.get_latest_analysis()
    return {
        "moving_averages": analysis["moving_averages"],
        "outliers": analysis["outliers"],
        "confidence": analysis["confidence"]
    }
```

## 🐳 Docker 구성

### 📦 Dockerfile (멀티스테이지 빌드)
```dockerfile
# 개발 스테이지
FROM python:3.9-slim as development
WORKDIR /app
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY . .
CMD ["python", "src/python/backend/main.py"]

# 운영 스테이지
FROM python:3.9-slim as production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.python.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 🔧 docker-compose.yml
```yaml
version: '3.8'
services:
  dht22-monitor:
    build:
      context: .
      target: production
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONPATH=/app
      - DATABASE_PATH=/app/data/climate_monitoring.db
    restart: unless-stopped

  dht22-dev:
    build:
      context: .
      target: development
    ports:
      - "8001:8000"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
      - DEBUG=true
```

## 📁 프로젝트 구조

```
04_P_dht22_monitoring/
├── src/
│   ├── arduino/
│   │   ├── dht22_simulator.ino          # DHT22 시뮬레이터
│   │   └── README.md
│   └── python/
│       ├── simulator/                    # Phase 1: 시뮬레이터
│       │   ├── __init__.py
│       │   ├── arduino_mock.py
│       │   ├── simulator_interface.py
│       │   └── test_simulator.py
│       └── backend/                      # Phase 2-4: 웹 백엔드
│           ├── main.py                   # FastAPI 메인 서버
│           ├── database.py               # 데이터베이스 관리
│           ├── data_analyzer.py          # 데이터 분석 엔진
│           ├── climate_calculator.py     # 기상 계산 유틸리티
│           └── requirements.txt
├── tests/
│   ├── test_database.py
│   ├── test_analyzer.py
│   └── test_calculator.py
├── docs/
│   ├── architecture/
│   │   └── 01_kiro_dht22_web_dashboard_architecture.md
│   └── api/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 🚀 개발 단계

### Phase 1: 시뮬레이터 개발
1. **Arduino DHT22 시뮬레이터** 구현
2. **Python Mock 시뮬레이터** 개발
3. **시뮬레이션 모드** 구현 (6가지 환경 조건)

### Phase 2: 백엔드 개발
1. **FastAPI 서버** 구축
2. **WebSocket 실시간 통신** 구현
3. **SQLite 데이터베이스** 설계 및 구현

### Phase 3: 데이터 분석
1. **이동평균 계산** 엔진
2. **이상치 탐지** 알고리즘 (Z-score, IQR)
3. **기상 계산** 유틸리티 (체감온도, 이슬점)

### Phase 4: 웹 대시보드
1. **실시간 대시보드** 구현
2. **히스토리 차트** 개발
3. **분석 패널** 구현
4. **알림 시스템** 구축

### Phase 5: 최적화 및 배포
1. **Docker 컨테이너화**
2. **성능 최적화**
3. **코드 품질 관리** (Ruff, Black)
4. **테스트 자동화**

## 🎯 성능 목표

### 📊 시스템 성능
- **데이터 수집 주기**: 1초
- **WebSocket 지연시간**: < 100ms
- **데이터베이스 응답시간**: < 50ms
- **메모리 사용량**: < 100MB
- **CPU 사용률**: < 10%

### 📈 확장성
- **동시 연결**: 최대 50개 WebSocket 연결
- **데이터 보관**: 48시간 (자동 정리)
- **히스토리 조회**: 최대 1000개 데이터 포인트

## 🔒 보안 고려사항

### 🛡️ 보안 기능
1. **API 문서 비활성화** (운영 환경)
2. **입력 데이터 검증** 및 새니타이징
3. **SQL 인젝션 방지** (파라미터화된 쿼리)
4. **CORS 정책** 적용
5. **로그 보안** (민감 정보 마스킹)

### 🔐 인증 및 권한 (향후 확장)
- **JWT 토큰** 기반 인증
- **역할 기반 접근 제어** (RBAC)
- **API 키** 관리

## 📋 테스트 전략

### 🧪 테스트 유형
1. **단위 테스트**: 각 모듈별 기능 테스트
2. **통합 테스트**: API 엔드포인트 테스트
3. **성능 테스트**: 부하 테스트 및 메모리 누수 검사
4. **E2E 테스트**: 전체 시스템 통합 테스트

### 📊 테스트 커버리지 목표
- **코드 커버리지**: > 80%
- **API 테스트**: 모든 엔드포인트
- **데이터베이스 테스트**: CRUD 작업 검증

## 📈 모니터링 및 로깅

### 📊 시스템 모니터링
- **시스템 리소스**: CPU, 메모리, 디스크 사용량
- **데이터베이스 성능**: 쿼리 실행 시간, 연결 수
- **WebSocket 연결**: 활성 연결 수, 메시지 처리량

### 📝 로깅 전략
```python
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "dht22_monitor.log",
            "formatter": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
```

---

## 📚 참고 자료

### 🔗 기술 문서
- [DHT22 센서 데이터시트](https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Chart.js 문서](https://www.chartjs.org/docs/)
- [SQLite 문서](https://sqlite.org/docs.html)

### 🌡️ 기상 계산 공식
- [Heat Index 계산](https://www.weather.gov/ama/heatindex)
- [Dew Point 계산](https://en.wikipedia.org/wiki/Dew_point)
- [이상치 탐지 알고리즘](https://en.wikipedia.org/wiki/Outlier)

---

*이 설계서는 INA219 전력 모니터링 시스템의 성공적인 아키텍처를 기반으로 DHT22 온습도 모니터링에 최적화하여 작성되었습니다.*