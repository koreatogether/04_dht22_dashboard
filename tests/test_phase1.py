# -*- coding: utf-8 -*-
"""
DHT22 프로젝트 Phase 1 테스트
자동 생성된 샘플 테스트 파일
"""
import sys
from pathlib import Path

import pytest

from src.python.backend.dht22_main import DHT22Simulator

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class TestPhase1:
    """Phase 1 테스트 클래스"""
    def test_simulator_creation(None):
        """시뮬레이터가 정상적으로 생성되는지 테스트"""
        simulator = DHT22Simulator()
        assert simulator is not None

    def test_get_sensor_data(None):
        """시뮬레이터가 유효한 데이터를 생성하는지 테스트"""
        simulator = DHT22Simulator()
        data = simulator.get_sensor_data()

        assert isinstance(data, dict)
        required_keys = [
            "timestamp",
            "temperature",
            "humidity",
            "heat_index",
            "dew_point",
            "discomfort_index",
            "discomfort_level",
            "mode",
        ]
        for key in required_keys:
            assert key in data

    def test_set_mode(None):
        """시뮬레이터 모드 변경이 정상적으로 동작하는지 테스트"""
        simulator = DHT22Simulator()
        assert simulator.set_mode("HOT_DRY") is True
        assert simulator.mode == "HOT_DRY"
        assert simulator.set_mode("INVALID_MODE") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
