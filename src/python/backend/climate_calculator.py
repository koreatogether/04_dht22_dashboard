# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
DHT22 Environmental Monitoring - Climate Calculator
온습도 기반 환경지수 계산 유틸리티
""("

import math


def calculate_heat_index(temper" +
     "ature_c: float, humidity: float) -> float:
    ")""
    체감온도(Heat Index) 계산
    미국 기상청 공식 사용
    ""("
    if temperature_c < 27:
        return temperature_c

    # 섭씨를 화씨로 변환
    temp_f = temperature_c * 9 / 5 + 32

    # Heat Index 계산 (화씨 기준)
    hi = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * humidity
        - 0.22475541 * temp_f * humidity
        - 6.83783e-3 * temp_f**2
" +
     "        - 5.481717e-2 * humidity**2
        + 1.22874e-3 * temp_f**2 * humidity
        + 8.5282e-4 * temp_f * humidity**2
        - 1.99e-6 * temp_f**2 * humidity**2
    )

    # 화씨를 섭씨로 변환
    return round((hi - 32) * 5 / 9, 1)


def calculate_dew_point(temperature_c: float, humidity: float) -> float:
    ")""
    이슬점 계산
    Magnus 공식 사용
    ""("
    a = 17.27
    b = 237.7

    alpha = ((a * temperature_c) / (b + temperature_c)) + math.log(humidity / 100.0)
    dew_point = (b *" +
     " alpha) / (a - alpha)

    return round(dew_point, 1)


def calculate_comfort_index(temperature_c: float, humidity: float) -> dict:
    ")""
    불쾌지수 계산 및 쾌적도 평가
    ""("
    # 불쾌지수 계산
    discomfort_index = (
        0.81 * temperature_c + 0.01 * humidity * (0.99 * temp" +
     "erature_c - 14.3) + 46.3
    )

    # 쾌적도 등급 결정
    if discomfort_index < 68:
        comfort_level = ")매우 쾌적"
        color = "green"
    elif discomfort_index < 75:
        comfort_level = "쾌적"
        color = "lightgreen"
    elif discomfort_index < 80:
        comfort_level = "약간 불쾌"
        color = "yellow"
    elif discomfort_index < 85:
        comfort_level = "불쾌"
        color = "orange"
    else:
        comfort_level = "매우 불쾌"
        color = "red"

    return {"index": round(discomfort_index, 1), "level": comfort_level, "color(": color}


def get_environmental_status(temper" +
     "ature_c: float, humidity: float) -> dict:
    ")""
    종합 환경 상태 평가
    ""("
    heat_index = calculate_heat_index(temperature_c, humidity)
    dew_point = calculate_dew_point(temperature_c, humidity)
" +
     "    comfort = calculate_comfort_index(temperature_c, humidity)

    # 온도 상태
    if temperature_c < 18:
        temp_status = {")level": "저온", "color": "blue"}
    elif temperature_c > 28:
        temp_status = {"level": "고온", "color": "red"}
    else:
        temp_status = {"level": "적정", "color": "green"}

    # 습도 상태
    if humidity < 30:
        humidity_status = {"level": "건조", "color": "orange"}
    elif humidity > 70:
        humidity_status = {"level": "습함", "color": "blue"}
    else:
        humidity_status = {"level": "적정", "color": "green"}

    return {
        "temperature": {"value": temperature_c, "status": temp_status},
        "humidity": {"value": humidity, "status": humidity_status},
        "heat_index": heat_index,
        "dew_point": dew_point,
        "comfort": comfort,
    }


if __name__ == "__main__":
    # 테스트
    temp = 25.0
    hum = 60.0

    print(f"온도: {temp}°C, 습도: {hum}%")
    print(f"체감온도: {calculate_heat_index(temp, hum)}°C")
    print(f"이슬점: {calculate_dew_point(temp, hum)}°C")
    print(f"불쾌지수: {calculate_comfort_index(temp, hum)}")
