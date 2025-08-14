# -*- coding: utf-8 -*-
"""
DHT22 프로젝트 Phase 4 테스트
- 데이터 분석 기능 테스트
"""
import pytest
import sys
from pathlib import Path
import numpy as np

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Placeholder for data analysis functions
def calculate_moving_average(data, window_size): -> None:
    if not data or window_size <= 0:
        return []
    return np.convolve(data, np.ones(window_size), 'valid') / window_size

class TestPhase4:
    """Phase 4 테스트 클래스"""

def test_moving_average_calculation(self): -> None:
        """이동 평균 계산 테스트"""
        data = [10, 20, 30, 40, 50, 60]
        moving_avg = calculate_moving_average(data, 3)
        assert np.allclose(moving_avg, [20., 30., 40., 50.])

def test_moving_average_empty_data(self): -> None:
        """빈 데이터에 대한 이동 평균 계산 테스트"""
        data = []
        moving_avg = calculate_moving_average(data, 3)
        assert len(moving_avg) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])