# -*- coding: utf-8 -*-
"""
기후 관련 계산 유틸리티
- 열지수 (Heat Index)
- 이슬점 (Dew Point)
- 불쾌지수 (Discomfort Index)
"""
import math


def calculate_heat_index(temp_c: float, humidity: float) -> float:
    """
    체감온도(열지수)를 계산합니다. (미국 국립 기상청(NOAA)의 Steadman 공식 사용)
    공식은 화씨(F)를 기준으로 하므로, 섭씨(C)를 화씨로 변환 후 계산하고 다시 섭씨로 변환합니다.
    """
    temp_f = (temp_c * 9 / 5) + 32
    if temp_f < 80.0:
        return temp_c

    heat_index_f = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * humidity
        - 0.22475541 * temp_f * humidity
        - 6.83783e-3 * temp_f**2
        - 5.481717e-2 * humidity**2
        + 1.22874e-3 * temp_f**2 * humidity
        + 8.5282e-4 * temp_f * humidity**2
        - 1.99e-6 * temp_f**2 * humidity**2
    )

    if humidity < 13 and 80 <= temp_f <= 112:
        adjustment = ((13 - humidity) / 4) * math.sqrt((17 - abs(temp_f - 95.0)) / 17)
        heat_index_f -= adjustment
    if humidity > 85 and 80 <= temp_f <= 87:
        adjustment = ((humidity - 85) / 10) * ((87 - temp_f) / 5)
        heat_index_f += adjustment

    return (heat_index_f - 32) * 5 / 9


def calculate_dew_point(temp_c: float, humidity: float) -> float:
    """
    이슬점을 계산합니다. (Magnus-Tetens 공식 근사치 사용)
    """
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return (b * alpha) / (a - alpha)


def calculate_discomfort_index(temp_c: float, humidity: float) -> float:
    """
    불쾌지수를 계산합니다. (Thom의 공식)
    DI = 0.81 * T + 0.01 * RH * (0.99 * T - 14.3) + 46.3
    """
    return 0.81 * temp_c + 0.01 * humidity * (0.99 * temp_c - 14.3) + 46.3


def get_discomfort_level(di: float) -> str:
    """불쾌지수 단계 판별"""
    if di >= 80:
        return "매우 높음 (전원 불쾌감)"
    elif di >= 75:
        return "높음 (50% 불쾌감)"
    elif di >= 68:
        return "보통 (10% 불쾌감)"
    else:
        return "낮음 (쾌적함)"


if __name__ == "__main__":
    temp = 28.0
    hum = 70.0
    hi = calculate_heat_index(temp, hum)
    dp = calculate_dew_point(temp, hum)
    di = calculate_discomfort_index(temp, hum)
    di_level = get_discomfort_level(di)
    print(f"온도: {temp}°C, 습도: {hum}%RH")
    print(f"체감온도(열지수): {hi:.2f}°C")
    print(f"이슬점: {dp:.2f}°C")
    print(f"불쾌지수: {di:.2f} ({di_level})")
