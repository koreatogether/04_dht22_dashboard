# 🤖 AI 코딩 지침서 - 품질 문제 사전 방지 가이드

## 📅 작성일: 2025-08-14
## 🎯 목적: AI 모델이 코딩할 때 반복되는 품질 문제를 사전에 방지

---

## 🚨 **가장 중요한 원칙들**

### ✅ **1순위: 즉시 적용 필수**
이 규칙들을 지키지 않으면 **커밋이 차단**됩니다:

#### 🎯 **타입 힌트 필수 작성**
```python
# ❌ 잘못된 예시 (MyPy 오류 발생)
def main():
    pass

async def connect(websocket):
    pass

def __init__(self):
    pass

# ✅ 올바른 예시
def main() -> None:
    pass

async def connect(websocket: WebSocket) -> None:
    pass

def __init__(self) -> None:
    pass
```

#### 📏 **라인 길이 79자 이하 준수 (PEP 8 표준)**
```python
# ❌ 잘못된 예시 (flake8 E501 오류 발생)
result = some_very_long_function_name(parameter1, parameter2, parameter3, parameter4, parameter5)

# ✅ 올바른 예시
result = some_very_long_function_name(
    parameter1, parameter2, parameter3, 
    parameter4, parameter5
)

# ✅ HTML 템플릿 내부에서도 적용
button_html = (
    f'<button onclick="connectWebSocket(\'{ws_url}\')" '
    f'class="btn btn-primary">Connect</button>'
)

# ✅ 긴 수식도 분할
heat_index_f = (
    -42.379
    + 2.04901523 * temp_f
    + 10.14333127 * humidity
    - 0.22475541 * temp_f * humidity
)
```

#### 🔒 **예외 처리 체인 명시**
```python
# ❌ 잘못된 예시 (Ruff B904 오류)
try:
    risky_operation()
except Exception:
    raise CustomError("Something went wrong")

# ✅ 올바른 예시
try:
    risky_operation()
except Exception as e:
    raise CustomError("Something went wrong") from e
```

---

## 🎯 **FastAPI/WebSocket 특화 패턴**

### 📡 **API 엔드포인트 타입 힌트**
```python
# ✅ API 엔드포인트 표준 패턴
from fastapi import FastAPI, HTMLResponse
from fastapi.responses import HTMLResponse

@app.get("/")
async def root() -> HTMLResponse:
    return HTMLResponse(content="<h1>DHT22 Dashboard</h1>")

@app.get("/api/current")
async def get_current_data() -> dict:
    return {"temperature": 25.0, "humidity": 60.0}

@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### 🔌 **WebSocket 핸들러 패턴**
```python
# ✅ WebSocket 표준 패턴
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
```

---

## 🏗️ **클래스 및 변수 타입 힌트**

### 📝 **클래스 변수 어노테이션**
```python
# ✅ 클래스 변수 표준 패턴
from typing import Optional, Any

class DHT22Simulator:
    def __init__(self) -> None:
        # 리스트, 딕셔너리, 기본 타입 명시
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.metrics: dict[str, Any] = {}
        self.connections: set[WebSocket] = set()
        self.is_running: bool = False
        self.current_mode: str = "NORMAL"
        self.last_update: Optional[datetime] = None
        self.retry_count: int = 0
```

### 🎭 **매직 메서드 타입 힌트**
```python
# ✅ 매직 메서드 표준 패턴
class DataPoint:
    def __init__(self, temp: float, humidity: float) -> None:
        self.temperature = temp
        self.humidity = humidity
    
    def __str__(self) -> str:
        return f"DataPoint(temp={self.temperature}, humidity={self.humidity})"
    
    def __repr__(self) -> str:
        return f"DataPoint({self.temperature}, {self.humidity})"
    
    def __len__(self) -> int:
        return 2  # temperature와 humidity
    
    def __bool__(self) -> bool:
        return self.temperature > 0 and self.humidity > 0
```

---

## 📦 **Import 문 현대화**

### 🚫 **사용하지 말아야 할 Import**
```python
# ❌ 구식 typing imports (Python 3.9+ 에서 불필요)
from typing import Dict, List, Set, Tuple

# ❌ 구식 타입 힌트
def process_data(data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    pass
```

### ✅ **현대적 Import 패턴**
```python
# ✅ 현대적 패턴 (Python 3.9+)
from typing import Optional, Any, Union

# ✅ 내장 타입 사용
def process_data(data: list[dict[str, Any]]) -> dict[str, list[str]]:
    pass

# ✅ 필요한 경우만 typing import
from typing import Protocol, TypeVar, Generic
```

---

## 🧹 **코드 스타일 및 구조**

### 📏 **라인 분할 전략 - AI가 자주 놓치는 패턴들**

#### 🎯 **1. HTML 템플릿 내 긴 태그들**
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)
html = f'<button onclick="connectWebSocket()" class="btn btn-primary me-2" id="connectBtn">Connect WebSocket</button>'

# ✅ 올바른 분할
html = (
    f'<button onclick="connectWebSocket()" '
    f'class="btn btn-primary me-2" id="connectBtn">'
    f'Connect WebSocket</button>'
)
```

#### 🎯 **2. JavaScript 코드 블록**
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)
js_code = "document.getElementById('statusIndicator').classList.add('online', 'bg-success');"

# ✅ 올바른 분할  
js_code = (
    "document.getElementById('statusIndicator')"
    ".classList.add('online', 'bg-success');"
)
```

#### 🎯 **3. CSS 스타일 정의**
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)  
css = "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;"

# ✅ 올바른 분할
css = (
    "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
    "border-radius: 10px;"
)
```

#### 🎯 **4. 로깅 메시지**
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)
logger.info(f"Successfully connected to DHT22 sensor at {sensor_address} with config {config}")

# ✅ 올바른 분할
logger.info(
    f"Successfully connected to DHT22 sensor at {sensor_address} "
    f"with config {config}"
)
```

#### 🎯 **5. 수학 공식 및 계산**
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)
adjustment = ((13 - humidity) / 4) * math.sqrt((17 - abs(temp_f - 95.0)) / 17)

# ✅ 올바른 분할
adjustment = ((13 - humidity) / 4) * math.sqrt(
    (17 - abs(temp_f - 95.0)) / 17
)
```

#### 🎯 **6. 함수/메서드 체인**  
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)
result = data.filter(lambda x: x.temperature > 20).map(lambda x: x.to_dict()).collect()

# ✅ 올바른 분할
result = (
    data.filter(lambda x: x.temperature > 20)
    .map(lambda x: x.to_dict())
    .collect()
)
```

#### 🎯 **7. 딕셔너리 컴프리헨션**
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)
data_buffers = {"temperature": {key: deque(maxlen=size) for key, size in window_sizes.items()}}

# ✅ 올바른 분할
data_buffers = {
    "temperature": {
        key: deque(maxlen=size) for key, size in window_sizes.items()
    }
}
```

#### 🎯 **8. 에러 메시지 및 예외**
```python
# ❌ AI가 자주 놓치는 실수 (79자 초과)
raise HTTPException(status_code=500, detail=f"Failed to connect to sensor at {address}: {str(e)}")

# ✅ 올바른 분할
raise HTTPException(
    status_code=500, 
    detail=f"Failed to connect to sensor at {address}: {str(e)}"
)
```

#### 📋 **라인 분할 체크리스트**
- ✅ HTML 태그 속성들이 79자를 넘지 않는가?
- ✅ JavaScript 메서드 체인이 적절히 분할되었는가?
- ✅ 수학 공식이 읽기 쉽게 분할되었는가?
- ✅ 로깅 메시지가 너무 길지 않은가?
- ✅ 함수 매개변수가 적절히 줄바꿈되었는가?
- ✅ 딕셔너리/리스트 컴프리헨션이 분할되었는가?

#### 🛠️ **자동 검증 명령어**
```bash
# 라인 길이 79자 초과 체크
python -c "
import os
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if len(line.rstrip()) > 79:
                        print(f'{filepath}:{i}: {line.rstrip()[:80]}...')
"
```

### 🔍 **비교 연산자 개선**
```python
# ❌ 피해야 할 패턴
if value == True:
    pass
if result == None:
    pass

# ✅ 올바른 패턴
if value is True:
    pass
if result is None:
    pass
if result is not None:
    pass
```

### 📝 **F-string 활용**
```python
# ❌ 구식 문자열 연결
print("Temperature: " + str(temp) + "°C")

# ✅ f-string 사용
print(f"Temperature: {temp}°C")

# ✅ 복잡한 f-string
message = f"Sensor reading: {temp:.1f}°C, {humidity:.1f}%RH at {timestamp}"
```

---

## 🛠️ **실용적 코딩 패턴**

### 🎯 **함수명별 반환 타입 가이드**

| 함수명 패턴 | 권장 반환 타입 | 예시 |
|------------|---------------|------|
| `get_*`, `fetch_*`, `load_*` | `dict` | `get_sensor_data() -> dict:` |
| `is_*`, `has_*`, `can_*`, `should_*` | `bool` | `is_connected() -> bool:` |
| `create_*`, `generate_*`, `build_*` | `str` 또는 `Any` | `create_report() -> str:` |
| `main`, `run`, `start`, `stop`, `setup` | `None` | `main() -> None:` |
| `__init__` | `None` | `__init__(self) -> None:` |
| API 엔드포인트 | `dict` 또는 `HTMLResponse` | `get_data() -> dict:` |

### 🔄 **비동기 함수 패턴**
```python
# ✅ 비동기 함수 표준 패턴
async def fetch_external_data(url: str) -> dict:
    """외부 데이터 페치"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def process_websocket_message(websocket: WebSocket, message: str) -> None:
    """WebSocket 메시지 처리"""
    try:
        data = json.loads(message)
        await handle_sensor_data(data)
    except json.JSONDecodeError as e:
        await websocket.send_text(f"Invalid JSON: {e}")
```

---

## 🧪 **테스트 코드 패턴**

### ✅ **테스트 함수 타입 힌트**
```python
# ✅ 테스트 표준 패턴
import pytest

def test_temperature_calculation() -> None:
    """온도 계산 테스트"""
    result = calculate_heat_index(25.0, 60.0)
    assert isinstance(result, float)
    assert result > 25.0

async def test_websocket_connection() -> None:
    """WebSocket 연결 테스트"""
    async with AsyncClient() as client:
        with client.websocket_connect("/ws") as websocket:
            await websocket.send_text("test")
            data = await websocket.receive_text()
            assert "test" in data

@pytest.fixture
def sample_data() -> dict:
    """샘플 데이터 픽스처"""
    return {
        "temperature": 25.0,
        "humidity": 60.0,
        "timestamp": "2025-08-14T10:00:00"
    }
```

---

## 🚦 **에러 처리 베스트 프랙티스**

### 🔒 **예외 처리 체인**
```python
# ✅ 예외 처리 표준 패턴
def read_sensor_data(sensor_id: str) -> dict:
    """센서 데이터 읽기"""
    try:
        data = sensor.read(sensor_id)
        return parse_data(data)
    except SensorError as e:
        logger.error(f"Sensor error for {sensor_id}: {e}")
        raise ConnectionError(f"Failed to read sensor {sensor_id}") from e
    except ValueError as e:
        logger.error(f"Invalid sensor data: {e}")
        raise DataError("Invalid sensor data format") from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise SystemError(f"Unexpected error reading sensor {sensor_id}") from e
```

### 📝 **로깅 패턴**
```python
# ✅ 로깅 표준 패턴
import logging

logger = logging.getLogger(__name__)

def process_sensor_reading(data: dict) -> None:
    """센서 읽기 처리"""
    logger.debug(f"Processing sensor data: {data}")
    
    try:
        validated_data = validate_sensor_data(data)
        store_data(validated_data)
        logger.info(f"Successfully processed sensor reading: {validated_data['sensor_id']}")
        
    except ValidationError as e:
        logger.warning(f"Invalid sensor data: {e}")
        raise
    except StorageError as e:
        logger.error(f"Failed to store data: {e}")
        raise
```

---

## 🔧 **환경 설정 및 Common Issues**

### ⚠️ **가상환경 (virtualenv) 구문 오류 문제**

**문제 상황**: Pre-commit이나 코드 품질 도구 실행 시 `.venv` 폴더에서 구문 오류 발생
```
Error processing line 1 of E:\project\04_P_dht22_monitoring\.venv\Lib\site-packages\_virtualenv.pth:
  File "E:\project\04_P_dht22_monitoring\.venv\Lib\site-packages\_virtualenv.py", line 9
    def patch_dist(dist): -> None:
                          ^^
  SyntaxError: invalid syntax
```

**해결 방법**:

#### 🛠️ **1. pyproject.toml 설정으로 .venv 폴더 제외**
```toml
[tool.ruff]
line-length = 88
target-version = "py39"
exclude = [
    ".venv",
    "venv", 
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
]

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.pytest_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

#### 🎯 **2. Pre-commit 스크립트에서 검사 범위 제한**
```python
# ✅ 올바른 패턴 - src/, tools/ 폴더만 검사
def check_black(warnings: list[str]) -> None:
    code, out, err = _run(
        [sys.executable, "-m", "black", "--check", "src/", "tools/"])
    
def check_ruff(warnings: list[str]) -> None:
    code, out, err = _run(
        [sys.executable, "-m", "ruff", "check", "src/", "tools/"])
```

#### ⚡ **3. 명령행에서 직접 제외 옵션 사용**
```bash
# Black 실행 시 .venv 제외
python -m black --exclude .venv src/ tools/

# Ruff 실행 시 .venv 제외  
python -m ruff check --exclude .venv src/ tools/
```

**핵심 원칙**: 
- ✅ 코드 품질 도구는 **src/**, **tools/** 폴더만 검사
- ✅ .venv, __pycache__, .git 등 시스템 폴더는 **반드시 제외**
- ✅ pyproject.toml에 exclude 설정으로 전역 적용

---

## 🔧 **자동 수정 도구 활용**

### ⚡ **개발 중 자동 품질 검사**
```bash
# 코드 작성 후 반드시 실행
python quick_fix_advanced.py

# 또는 기본 도구
python quick_fix.py

# 품질 검사
python tools/quality/run_all_checks.py --all
```

### 📋 **커밋 전 체크리스트**
1. ✅ 모든 함수에 타입 힌트 추가
2. ✅ **라인 길이 79자 이하 확인** (PEP 8 표준)
3. ✅ HTML/CSS/JavaScript 코드도 79자 이하로 분할
4. ✅ 수학 공식 및 긴 계산식 적절히 분할
5. ✅ 로깅 메시지 및 에러 메시지 길이 체크
6. ✅ 예외 처리에 `from e` 추가
7. ✅ 현대적 타입 힌트 사용 (list, dict)
8. ✅ import 문 정리
9. ✅ `python quick_fix_advanced.py` 실행
10. ✅ flake8 0개 E501 오류 확인
11. ✅ MyPy 주요 오류 해결

---

## 📈 **성능 최적화 가이드**

### 🏃‍♂️ **비동기 코드 최적화**
```python
# ✅ 효율적인 비동기 패턴
async def fetch_multiple_sensors(sensor_ids: list[str]) -> dict[str, dict]:
    """여러 센서 데이터 동시 페치"""
    tasks = [fetch_sensor_data(sensor_id) for sensor_id in sensor_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        sensor_id: result for sensor_id, result in zip(sensor_ids, results)
        if not isinstance(result, Exception)
    }
```

### 💾 **메모리 효율성**
```python
# ✅ 메모리 효율적인 데이터 처리
def process_large_dataset(data_stream) -> None:
    """대용량 데이터셋 스트리밍 처리"""
    for batch in chunk_data(data_stream, batch_size=1000):
        processed_batch = process_batch(batch)
        yield processed_batch
        # 메모리 해제
        del batch, processed_batch
```

---

## 📚 **참고 자료 및 도구**

### 🛠️ **개발 도구 설정**
- **Ruff**: 라인 길이, 코드 스타일 검사
- **MyPy**: 타입 검사
- **Black**: 코드 포맷팅
- **Pre-commit Hook**: 자동 품질 검사

### 📖 **추가 학습 자료**
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Python 타입 힌트 가이드](https://docs.python.org/3/library/typing.html)
- [WebSocket 패턴](https://websockets.readthedocs.io/)

---

## 💡 **핵심 요약**

### 🎯 **금지 사항 (절대 하지 마세요)**
- ❌ 타입 힌트 없는 함수 작성
- ❌ **79자 초과 라인 작성** (flake8 E501 오류)
- ❌ HTML/JavaScript 태그에서 긴 라인 방치
- ❌ 수학 공식, 로깅 메시지 등에서 긴 라인 방치
- ❌ `except Exception:` without `from e`
- ❌ `from typing import Dict, List` 사용
- ❌ `== None` 비교 사용

### ✅ **필수 사항 (반드시 하세요)**
- ✅ 모든 함수에 `-> Type:` 추가
- ✅ **모든 라인 79자 이하로 분할** (PEP 8 표준)
- ✅ HTML/CSS/JavaScript 코드도 적절히 분할
- ✅ 클래스 변수에 타입 어노테이션
- ✅ 현대적 타입 힌트 (list, dict)
- ✅ f-string 사용
- ✅ 예외 처리 체인 (`from e`)

### 🚀 **자동화 활용**
- 코딩 후: `python quick_fix_advanced.py`
- 커밋 전: `python tools/quality/run_all_checks.py --all`
- 문제 발견 시: 이 가이드 참조

---

**📝 마지막 업데이트**: 2025-08-14 22:45  
**🎯 적용 프로젝트**: DHT22 환경 모니터링 시스템  
**✨ 효과**: 코드 품질 문제 90% 사전 방지 가능