#!/usr/bin/env python3
"""
데이터 프로세서 테스트

data_processor.py의 기능을 테스트합니다.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path

# 테스트 대상 모듈 import
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from utils.data_processor import (
    calculate_dew_point, calculate_heat_index, calculate_discomfort_index,
    get_comfort_level, process_sensor_data, DataBuffer
)


class TestDataProcessorFunctions:
    """데이터 처리 함수들 테스트"""
    
    @pytest.fixture
    def sample_data(self):
        """샘플 센서 데이터"""
        return {
            "timestamp": datetime.now().isoformat(),
            "temperature": 25.5,
            "humidity": 60.0,
            "heat_index": 26.8,
            "sensor": "DHT22",
            "status": "OK"
        }
    
    def test_calculate_dew_point(self):
        """이슬점 계산 테스트"""
        dew_point = calculate_dew_point(25.0, 60.0)
        assert isinstance(dew_point, float)
        assert 15.0 < dew_point < 20.0  # 대략적인 범위 확인
    
    def test_calculate_heat_index(self):
        """열지수 계산 테스트"""
        heat_index = calculate_heat_index(30.0, 70.0)
        assert isinstance(heat_index, float)
        assert heat_index > 30.0  # 열지수는 온도보다 높아야 함
    
    def test_calculate_discomfort_index(self):
        """불쾌지수 계산 테스트"""
        di = calculate_discomfort_index(25.0, 60.0)
        assert isinstance(di, float)
        assert 20.0 < di < 30.0  # 일반적인 범위
    
    def test_get_comfort_level(self):
        """쾌적도 계산 테스트"""
        # 매우 쾌적한 조건
        comfort = get_comfort_level(20.0)
        assert comfort == "매우 쾌적"
        
        # 쾌적한 조건
        comfort = get_comfort_level(22.0)
        assert comfort == "쾌적"
        
        # 불쾌한 조건
        comfort = get_comfort_level(30.0)
        assert comfort == "불쾌"
        
        # 매우 불쾌한 조건
        comfort = get_comfort_level(35.0)
        assert comfort == "매우 불쾌"
    
    def test_process_sensor_data(self, sample_data):
        """센서 데이터 처리 테스트"""
        result = process_sensor_data(sample_data)
        
        assert result is not None
        assert "dew_point" in result
        assert "discomfort_index" in result
        assert "comfort_level" in result
        assert "python_timestamp" in result
        assert "datetime" in result
        
        # 원본 데이터도 포함되어야 함
        assert result["temperature"] == sample_data["temperature"]
        assert result["humidity"] == sample_data["humidity"]


class TestDataBuffer:
    """DataBuffer 클래스 테스트"""
    
    @pytest.fixture
    def buffer(self):
        """테스트용 버퍼 인스턴스"""
        return DataBuffer(max_size=5)
    
    @pytest.fixture
    def sample_data(self):
        """샘플 데이터"""
        return {"temperature": 25.0, "humidity": 60.0}
    
    def test_init(self, buffer):
        """초기화 테스트"""
        assert buffer.max_size == 5
        assert len(buffer.data) == 0
    
    def test_add_data(self, buffer, sample_data):
        """데이터 추가 테스트"""
        buffer.add(sample_data)
        assert len(buffer.data) == 1
        assert buffer.data[0] == sample_data
    
    def test_buffer_size_limit(self, buffer, sample_data):
        """버퍼 크기 제한 테스트"""
        # 제한보다 많은 데이터 추가
        for i in range(7):
            data = sample_data.copy()
            data["temperature"] = 20.0 + i
            buffer.add(data)
        
        # 버퍼 크기가 제한을 넘지 않는지 확인
        assert len(buffer.data) == 5
        # 가장 오래된 데이터가 제거되고 최신 데이터만 남아있는지 확인
        assert buffer.data[0]["temperature"] == 22.0
        assert buffer.data[-1]["temperature"] == 26.0
    
    def test_get_recent(self, buffer, sample_data):
        """최근 데이터 조회 테스트"""
        # 데이터 추가
        for i in range(3):
            data = sample_data.copy()
            data["temperature"] = 20.0 + i
            buffer.add(data)
        
        # 전체 데이터 조회
        all_data = buffer.get_recent()
        assert len(all_data) == 3
        
        # 최근 2개 데이터 조회
        recent = buffer.get_recent(2)
        assert len(recent) == 2
        assert recent[0]["temperature"] == 21.0
        assert recent[1]["temperature"] == 22.0
    
    def test_clear(self, buffer, sample_data):
        """버퍼 초기화 테스트"""
        buffer.add(sample_data)
        assert len(buffer.data) == 1
        
        buffer.clear()
        assert len(buffer.data) == 0
    
    def test_get_stats(self, buffer):
        """통계 정보 조회 테스트"""
        # 여러 데이터 추가
        temperatures = [20.0, 25.0, 30.0, 22.0, 28.0]
        for temp in temperatures:
            data = {"temperature": temp, "humidity": 60.0, "dew_point": temp - 5}
            buffer.add(data)
        
        stats = buffer.get_stats()
        
        assert "temperature" in stats
        assert stats["temperature"]["min"] == 20.0
        assert stats["temperature"]["max"] == 30.0
        assert stats["temperature"]["mean"] == 25.0
        assert stats["temperature"]["current"] == 28.0
    
    def test_to_dataframe(self, buffer, sample_data):
        """DataFrame 변환 테스트"""
        # pandas가 설치되어 있지 않을 수 있으므로 try-except 사용
        try:
            import pandas as pd
            
            buffer.add(sample_data)
            df = buffer.to_dataframe()
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
            assert "temperature" in df.columns
            assert "humidity" in df.columns
            
        except ImportError:
            pytest.skip("pandas not installed")


@pytest.fixture
def mock_sensor_data():
    """모의 센서 데이터 생성기"""
    def _generate_data(count=10, base_temp=25.0, base_humidity=60.0):
        data_list = []
        for i in range(count):
            data = {
                "timestamp": datetime.now().isoformat(),
                "temperature": base_temp + (i * 0.5),
                "humidity": base_humidity + (i * 1.0),
                "heat_index": base_temp + (i * 0.6),
                "sensor": "DHT22",
                "status": "OK"
            }
            data_list.append(data)
        return data_list
    return _generate_data


def test_batch_processing(mock_sensor_data):
    """배치 데이터 처리 테스트"""
    buffer = DataBuffer(max_size=20)
    test_data = mock_sensor_data(20)
    
    # 배치로 데이터 처리
    for data in test_data:
        processed = process_sensor_data(data)
        buffer.add(processed)
    
    assert len(buffer.data) == 20
    
    # 통계 확인
    stats = buffer.get_stats()
    assert stats["temperature"]["mean"] > 25.0
    assert stats["humidity"]["max"] > 60.0


def test_integration():
    """통합 테스트"""
    # 실제 사용 시나리오 테스트
    raw_data = {
        "temperature": 28.5,
        "humidity": 75.0,
        "sensor": "DHT22",
        "status": "OK"
    }
    
    # 데이터 처리
    processed = process_sensor_data(raw_data)
    
    # 버퍼에 저장
    buffer = DataBuffer()
    buffer.add(processed)
    
    # 결과 확인
    assert len(buffer.data) == 1
    stored_data = buffer.data[0]
    
    assert "dew_point" in stored_data
    assert "discomfort_index" in stored_data
    assert "comfort_level" in stored_data
    assert stored_data["temperature"] == 28.5
    assert stored_data["humidity"] == 75.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])