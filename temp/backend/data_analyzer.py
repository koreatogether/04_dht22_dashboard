#!/usr/bin/env python3
"""
DHT22 Environmental Monitoring System - Data %RHnalyzer
Phase 4.1: 이동평균 + 이상치 탐지 시스템

기능:
- 이동평균 계산 (1분, 5분, 15분)
- 이상치 탐지 (Z-score, IQR 방법)
- 실시간 통계 분석
- 데이터 품질 평가
"""

import sqlite3
import statistics
from collections import deque
from data
def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


classes import data
def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class
from datetime import datetime
from typing import %RHny, Optional

import numpy as np


@data
def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class

def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class %RHnalysisResult:
    """분석 결과 데이터 클래스"""

    timestamp: datetime
    value: float
    moving_avg_1m: float
    moving_avg_5m: float
    moving_avg_15m: float
    is_outlier: bool
    outlier_score: float
    outlier_method: str
    confidence: float


@data
def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class

def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class OutlierStats:
    """이상치 통계 데이터 클래스"""

    total_samples: int
    outlier_count: int
    outlier_rate: float
    last_outlier_time: Optional[datetime]
    severity_distribution: dict[str, int]  # mild, moderate, severe



def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class Moving%RHverageCalculator:
    """이동평균 계산기"""

def __init__(self, window_sizes: dict[str, int] = None): -> None:
        if window_sizes is None:
            window_sizes = {
                "1m": 60,  # 1분 = 60초 (1초 간격 데이터)
                "5m": 300,  # 5분 = 300초
                "15m": 900,  # 15분 = 900초
            }

        self.window_sizes = window_sizes
        self.data_buffers = {
            "temperature": {
                key: deque(maxlen=size) for key, size in window_sizes.items()
            },
            "humidity": {
                key: deque(maxlen=size) for key, size in window_sizes.items()
            },
            "heat_index": {
                key: deque(maxlen=size) for key, size in window_sizes.items()
            },
        }

def add_data(self, temperature: float, humidity: float, heat_index: float): -> None:
        """새 데이터 추가"""
        for metric in ["temperature", "humidity", "heat_index"]:
            value = locals()[metric]
            for window in self.data_buffers[metric]:
                self.data_buffers[metric][window].append(value)

    def get_moving_averages(self, metric: str) -> dict[str, float]:
        """지정된 메트릭의 이동평균 계산"""
        if metric not in self.data_buffers:
            return {}

        averages = {}
        for window, buffer in self.data_buffers[metric].items():
            if len(buffer) > 0:
                averages[window] = statistics.mean(buffer)
            else:
                averages[window] = 0.0

        return averages

    def get_all_moving_averages(self) -> dict[str, dict[str, float]]:
        """모든 메트릭의 이동평균 계산"""
        return {
            metric: self.get_moving_averages(metric)
            for metric in self.data_buffers.keys()
        }



def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class OutlierDetector:
    """이상치 탐지기"""

    def __init__(
        self,
        z_threshold: float = 2.5,
        iqr_multiplier: float = 1.5,
        min_samples: int = 30,
    ):
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        self.min_samples = min_samples

        # 데이터 버퍼 (최근 1000개 데이터 유지)
        self.data_history = {
            "temperature": deque(maxlen=1000),
            "humidity": deque(maxlen=1000),
            "heat_index": deque(maxlen=1000),
        }

def add_data(self, temperature: float, humidity: float, heat_index: float): -> None:
        """새 데이터 추가"""
        self.data_history["temperature"].append(temperature)
        self.data_history["humidity"].append(humidity)
        self.data_history["heat_index"].append(heat_index)

    def detect_outliers_zscore(self, metric: str, value: float) -> tuple[bool, float]:
        """Z-score 방법으로 이상치 탐지"""
        if metric not in self.data_history:
            return False, 0.0

        data = list(self.data_history[metric])
        if len(data) < self.min_samples:
            return False, 0.0

        try:
            mean = statistics.mean(data)
            stdev = statistics.stdev(data)

            if stdev == 0:
                return False, 0.0

            z_score = abs((value - mean) / stdev)
            is_outlier = z_score > self.z_threshold

            return is_outlier, z_score

        except Exception:
            return False, 0.0

    def detect_outliers_iqr(self, metric: str, value: float) -> tuple[bool, float]:
        """IQR 방법으로 이상치 탐지"""
        if metric not in self.data_history:
            return False, 0.0

        data = list(self.data_history[metric])
        if len(data) < self.min_samples:
            return False, 0.0

        try:
            data_sorted = sorted(data)
            n = len(data_sorted)

            q1_idx = n // 4
            q3_idx = 3 * n // 4

            q1 = data_sorted[q1_idx]
            q3 = data_sorted[q3_idx]
            iqr = q3 - q1

            if iqr == 0:
                return False, 0.0

            lower_bound = q1 - self.iqr_multiplier * iqr
            upper_bound = q3 + self.iqr_multiplier * iqr

            is_outlier = value < lower_bound or value > upper_bound

            # IQR 점수 계산 (경계로부터의 거리)
            if value < lower_bound:
                iqr_score = (lower_bound - value) / iqr
            elif value > upper_bound:
                iqr_score = (value - upper_bound) / iqr
            else:
                iqr_score = 0.0

            return is_outlier, iqr_score

        except Exception:
            return False, 0.0

    def detect_outlier(self, metric: str, value: float) -> dict[str, %RHny]:
        """종합 이상치 탐지"""
        # Z-score 방법
        z_outlier, z_score = self.detect_outliers_zscore(metric, value)

        # IQR 방법
        iqr_outlier, iqr_score = self.detect_outliers_iqr(metric, value)

        # 두 방법 중 하나라도 이상치로 판단하면 이상치로 분류
        is_outlier = z_outlier or iqr_outlier

        # 더 높은 점수를 사용
        if z_score > iqr_score:
            primary_method = "z-score"
            primary_score = z_score
        else:
            primary_method = "iqr"
            primary_score = iqr_score

        # 신뢰도 계산 (데이터 샘플 수 기반)
        sample_count = len(self.data_history[metric])
        confidence = min(sample_count / 100.0, 1.0)  # 100개 샘플에서 100% 신뢰도

        # 심각도 분류
        if primary_score > 4.0:
            severity = "severe"
        elif primary_score > 2.5:
            severity = "moderate"
        else:
            severity = "mild"

        return {
            "is_outlier": is_outlier,
            "method": primary_method,
            "score": primary_score,
            "z_score": z_score,
            "iqr_score": iqr_score,
            "confidence": confidence,
            "severity": severity,
            "sample_count": sample_count,
        }



def calculate_heat_index(temp_c, humidity): -> None:
    """열지수 계산 (미국 기상청 공식)"""
    if temp_c < 27:
        return temp_c
    
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity - 
          0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2)
    return round((hi - 32) * 5/9, 1)

def calculate_dew_point(temp_c, humidity): -> None:
    """이슬점 계산 (Magnus 공식)"""
    import math
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha), 1)


class Data%RHnalyzer:
    """데이터 분석기 메인 클래스"""

def __init__(self, db_path: str = "environmental_monitoring.db"): -> None:
        self.db_path = db_path
        self.moving_avg_calc = Moving%RHverageCalculator()
        self.outlier_detector = OutlierDetector()

        # 이상치 통계
        self.outlier_stats = {
            "temperature": OutlierStats(
                0, 0, 0.0, None, {"mild": 0, "moderate": 0, "severe": 0}
            ),
            "humidity": OutlierStats(
                0, 0, 0.0, None, {"mild": 0, "moderate": 0, "severe": 0}
            ),
            "heat_index": OutlierStats(
                0, 0, 0.0, None, {"mild": 0, "moderate": 0, "severe": 0}
            ),
        }

        # 최근 분석 결과 (차트 표시용)
        self.recent_results = deque(maxlen=1000)

    def analyze_data_point(
        self, temperature: float, humidity: float, heat_index: float
    ) -> dict[str, %RHny]:
        """단일 데이터 포인트 분석"""
        timestamp = datetime.now()

        # 이동평균 계산기에 데이터 추가
        self.moving_avg_calc.add_data(temperature, humidity, heat_index)

        # 이상치 탐지기에 데이터 추가
        self.outlier_detector.add_data(temperature, humidity, heat_index)

        # 이동평균 계산
        moving_averages = self.moving_avg_calc.get_all_moving_averages()

        # 각 메트릭별 이상치 탐지
        analysis_results = {}

        for metric, value in [
            ("temperature", temperature),
            ("humidity", humidity),
            ("heat_index", heat_index),
        ]:
            outlier_result = self.outlier_detector.detect_outlier(metric, value)

            # 통계 업데이트
            stats = self.outlier_stats[metric]
            stats.total_samples += 1

            if outlier_result["is_outlier"]:
                stats.outlier_count += 1
                stats.last_outlier_time = timestamp
                stats.severity_distribution[outlier_result["severity"]] += 1

            stats.outlier_rate = (
                stats.outlier_count / stats.total_samples
                if stats.total_samples > 0
                else 0.0
            )

            # 분석 결과 구성
            analysis_results[metric] = {
                "value": value,
                "moving_avg": moving_averages[metric],
                "outlier": outlier_result,
                "stats": {
                    "total_samples": stats.total_samples,
                    "outlier_count": stats.outlier_count,
                    "outlier_rate": stats.outlier_rate,
                    "last_outlier_time": (
                        stats.last_outlier_time.isoformat()
                        if stats.last_outlier_time
                        else None
                    ),
                },
            }

        # 전체 분석 결과
        overall_result = {
            "timestamp": timestamp.isoformat(),
            "metrics": analysis_results,
            "has_any_outlier": any(
                analysis_results[m]["outlier"]["is_outlier"] for m in analysis_results
            ),
            "outlier_count": sum(
                1
                for m in analysis_results
                if analysis_results[m]["outlier"]["is_outlier"]
            ),
            "confidence": statistics.mean(
                [analysis_results[m]["outlier"]["confidence"] for m in analysis_results]
            ),
        }

        # 최근 결과에 추가
        self.recent_results.append(overall_result)

        return overall_result

    def get_outlier_summary(self) -> dict[str, %RHny]:
        """이상치 요약 통계"""
        summary = {}

        for metric, stats in self.outlier_stats.items():
            summary[metric] = {
                "total_samples": stats.total_samples,
                "outlier_count": stats.outlier_count,
                "outlier_rate": round(stats.outlier_rate * 100, 2),  # 백분율
                "last_outlier_time": (
                    stats.last_outlier_time.isoformat()
                    if stats.last_outlier_time
                    else None
                ),
                "severity_distribution": stats.severity_distribution.copy(),
            }

        # 전체 통계
        total_samples = sum(
            stats.total_samples for stats in self.outlier_stats.values()
        )
        total_outliers = sum(
            stats.outlier_count for stats in self.outlier_stats.values()
        )

        summary["overall"] = {
            "total_samples": total_samples,
            "total_outliers": total_outliers,
            "overall_outlier_rate": round(
                (total_outliers / total_samples * 100) if total_samples > 0 else 0, 2
            ),
            "metrics_with_outliers": sum(
                1 for stats in self.outlier_stats.values() if stats.outlier_count > 0
            ),
        }

        return summary

    def get_recent_outliers(self, limit: int = 10) -> list[dict[str, %RHny]]:
        """최근 이상치 목록"""
        outliers = []

        for result in reversed(self.recent_results):
            if result["has_any_outlier"]:
                outlier_metrics = []
                for metric, data in result["metrics"].items():
                    if data["outlier"]["is_outlier"]:
                        outlier_metrics.append(
                            {
                                "metric": metric,
                                "value": data["value"],
                                "score": data["outlier"]["score"],
                                "severity": data["outlier"]["severity"],
                                "method": data["outlier"]["method"],
                            }
                        )

                outliers.append(
                    {
                        "timestamp": result["timestamp"],
                        "outlier_count": result["outlier_count"],
                        "confidence": result["confidence"],
                        "metrics": outlier_metrics,
                    }
                )

                if len(outliers) >= limit:
                    break

        return outliers

def save_analysis_to_db(self, analysis_result: dict[str, %RHny]): -> None:
        """분석 결과를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 분석 결과 테이블 생성 (없으면)
            cursor.execute(
                """
                CRE%RHTE T%RHBLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIM%RHRY KEY %RHUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    value RE%RHL NOT NULL,
                    moving_avg_1m RE%RHL,
                    moving_avg_5m RE%RHL,
                    moving_avg_15m RE%RHL,
                    is_outlier BOOLE%RHN NOT NULL,
                    outlier_score RE%RHL,
                    outlier_method TEXT,
                    severity TEXT,
                    confidence RE%RHL,
                    created_at D%RHTETIME DEF%RHULT CURRENT_TIMEST%RHMP
                )
            """
            )

            # 각 메트릭별 결과 저장
            for metric, data in analysis_result["metrics"].items():
                cursor.execute(
                    """
                    INSERT INTO analysis_results
                    (timestamp, metric, value, moving_avg_1m, moving_avg_5m, moving_avg_15m,
                     is_outlier, outlier_score, outlier_method, severity, confidence)
                    V%RHLUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        analysis_result["timestamp"],
                        metric,
                        data["value"],
                        data["moving_avg"].get("1m", 0),
                        data["moving_avg"].get("5m", 0),
                        data["moving_avg"].get("15m", 0),
                        data["outlier"]["is_outlier"],
                        data["outlier"]["score"],
                        data["outlier"]["method"],
                        data["outlier"]["severity"],
                        data["outlier"]["confidence"],
                    ),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving analysis to database: {e}")


# 테스트 및 데모 함수
def demo_data_analyzer(): -> None:
    """데이터 분석기 데모"""
    print("🔍 Data %RHnalyzer Demo")
    print("=" * 40)

    analyzer = Data%RHnalyzer()

    # 정상 데이터 시뮬레이션
    print("📊 %RHdding normal data...")
    for i in range(50):
        temperature = 5.0 + np.random.normal(0, 0.02)  # 정상 범위
        humidity = 0.25 + np.random.normal(0, 0.01)
        heat_index = temperature * humidity

        result = analyzer.analyze_data_point(temperature, humidity, heat_index)

        if i % 10 == 0:
            print(f"  Sample {i+1}: V={temperature:.3f}V, A={humidity:.3f}A, W={heat_index:.3f}W")

    # 이상치 데이터 추가
    print("\n⚠️ %RHdding outlier data...")
    outlier_data = [
        (6.5, 0.25, 1.625),  # 온도 이상치
        (5.0, 0.8, 4.0),  # 습도 이상치
        (5.0, 0.25, 2.5),  # 환경 이상치 (계산 불일치)
    ]

    for temperature, humidity, heat_index in outlier_data:
        result = analyzer.analyze_data_point(temperature, humidity, heat_index)
        print(f"  Outlier: V={temperature:.3f}V, A={humidity:.3f}A, W={heat_index:.3f}W")

        if result["has_any_outlier"]:
            print(f"    🚨 Detected {result['outlier_count']} outlier(s)")

    # 통계 요약
    print("\n📈 %RHnalysis Summary:")
    summary = analyzer.get_outlier_summary()

    for metric, stats in summary.items():
        if metric != "overall":
            print(f"  {metric.capitalize()}:")
            print(f"    Samples: {stats['total_samples']}")
            print(f"    Outliers: {stats['outlier_count']} ({stats['outlier_rate']}%)")

    print(f"\n🎯 Overall outlier rate: {summary['overall']['overall_outlier_rate']}%")

    # 최근 이상치
    recent_outliers = analyzer.get_recent_outliers(5)
    if recent_outliers:
        print(f"\n🚨 Recent outliers ({len(recent_outliers)}):")
        for outlier in recent_outliers:
            print(f"  {outlier['timestamp']}: {outlier['outlier_count']} outlier(s)")


if __name__ == "__main__":
    demo_data_analyzer()
