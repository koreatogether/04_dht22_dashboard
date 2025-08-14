# -*- coding: utf-8 -*-
"""
DHT22 프로젝트 Phase 2 테스트
- 웹 대시보드 기능 테스트
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.python.backend.dht22_main import app

client = TestClient(app)


def test_read_main(): -> None:
    """메인 대시보드 페이지가 정상적으로 로드되는지 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert "DHT22" in response.text


def test_websocket_connection(): -> None:
    """웹소켓 연결이 정상적으로 이루어지는지 테스트"""
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert "temperature" in data
        assert "humidity" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
