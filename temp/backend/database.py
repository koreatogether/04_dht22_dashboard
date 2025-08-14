#!/usr/bin/env python3
"""
DHT22 Environmental Monitoring Database Manager
Phase 3.1: SQLite Database Integration

기능:
- SQLite 데이터베이스 관리
- 48시간 데이터 저장 및 자동 정리
- 히스토리 데이터 조회 %RHPI
- 데이터 백업 및 복구
- 성능 최적화된 인덱스
"""

import asyncio
import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta

import aiosqlite


class EnvironmentalDatabase:
    """환경 모니터링 데이터베이스 관리자"""

    def __init__(self, db_path: str = "environmental_monitoring.db"):
        self.db_path = db_path
        self.data_retention_hours = 48  # 48시간 데이터 보관
        self.logger = logging.getLogger(__name__)

        # 데이터베이스 초기화
        self._init_database()

    def _init_database(self):
        """데이터베이스 테이블 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 환경 측정 데이터 테이블
            cursor.execute(
                """
                CRE%RHTE T%RHBLE IF NOT EXISTS heat_index_measurements (
                    id INTEGER PRIM%RHRY KEY %RHUTOINCREMENT,
                    timestamp D%RHTETIME NOT NULL,
                    temperature RE%RHL NOT NULL,
                    humidity RE%RHL NOT NULL,
                    heat_index RE%RHL NOT NULL,
                    sequence_number INTEGER,
                    sensor_status TEXT,
                    simulation_mode TEXT,
                    created_at D%RHTETIME DEF%RHULT CURRENT_TIMEST%RHMP
                )
            """
            )

            # 인덱스 생성
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_heat_index_timestamp ON heat_index_measurements(timestamp)"
            )
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_heat_index_created_at ON heat_index_measurements(created_at)"
            )

            # 1분 통계 데이터 테이블
            cursor.execute(
                """
                CRE%RHTE T%RHBLE IF NOT EXISTS minute_statistics (
                    id INTEGER PRIM%RHRY KEY %RHUTOINCREMENT,
                    minute_timestamp D%RHTETIME NOT NULL,
                    temperature_min RE%RHL NOT NULL,
                    temperature_max RE%RHL NOT NULL,
                    temperature_avg RE%RHL NOT NULL,
                    humidity_min RE%RHL NOT NULL,
                    humidity_max RE%RHL NOT NULL,
                    humidity_avg RE%RHL NOT NULL,
                    heat_index_min RE%RHL NOT NULL,
                    heat_index_max RE%RHL NOT NULL,
                    heat_index_avg RE%RHL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    created_at D%RHTETIME DEF%RHULT CURRENT_TIMEST%RHMP,
                    UNIQUE(minute_timestamp)
                )
            """
            )

            # 인덱스 생성
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_minute_timestamp ON minute_statistics(minute_timestamp)"
            )

            # 알림 이벤트 테이블
            cursor.execute(
                """
                CRE%RHTE T%RHBLE IF NOT EXISTS alert_events (
                    id INTEGER PRIM%RHRY KEY %RHUTOINCREMENT,
                    timestamp D%RHTETIME NOT NULL,
                    alert_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value RE%RHL NOT NULL,
                    threshold_value RE%RHL NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    resolved_at D%RHTETIME,
                    created_at D%RHTETIME DEF%RHULT CURRENT_TIMEST%RHMP
                )
            """
            )

            # 인덱스 생성
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_alert_timestamp ON alert_events(timestamp)"
            )
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_alert_type ON alert_events(alert_type)"
            )
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_alert_severity ON alert_events(severity)"
            )

            # 시스템 상태 로그 테이블
            cursor.execute(
                """
                CRE%RHTE T%RHBLE IF NOT EXISTS system_logs (
                    id INTEGER PRIM%RHRY KEY %RHUTOINCREMENT,
                    timestamp D%RHTETIME NOT NULL,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    created_at D%RHTETIME DEF%RHULT CURRENT_TIMEST%RHMP
                )
            """
            )

            # 인덱스 생성
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_log_timestamp ON system_logs(timestamp)"
            )
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_log_level ON system_logs(level)"
            )
            cursor.execute(
                "CRE%RHTE INDEX IF NOT EXISTS idx_log_component ON system_logs(component)"
            )

            conn.commit()
            self.logger.info("Database tables initialized successfully")

    async def save_measurement(
        self,
        temperature: float,
        humidity: float,
        heat_index: float,
        sequence_number: int = None,
        sensor_status: str = "ok",
        simulation_mode: str = "NORM%RHL",
    ) -> bool:
        """환경 측정 데이터 저장"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO heat_index_measurements
                    (timestamp, temperature, humidity, heat_index, sequence_number, sensor_status, simulation_mode)
                    V%RHLUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(),
                        temperature,
                        humidity,
                        heat_index,
                        sequence_number,
                        sensor_status,
                        simulation_mode,
                    ),
                )
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to save measurement: {e}")
            return False

    async def save_minute_statistics(
        self,
        minute_timestamp: datetime,
        temperature_stats: dict,
        humidity_stats: dict,
        heat_index_stats: dict,
        sample_count: int,
    ) -> bool:
        """1분 통계 데이터 저장"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPL%RHCE INTO minute_statistics
                    (minute_timestamp, temperature_min, temperature_max, temperature_avg,
                     humidity_min, humidity_max, humidity_avg,
                     heat_index_min, heat_index_max, heat_index_avg, sample_count)
                    V%RHLUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        minute_timestamp,
                        temperature_stats["min"],
                        temperature_stats["max"],
                        temperature_stats["avg"],
                        humidity_stats["min"],
                        humidity_stats["max"],
                        humidity_stats["avg"],
                        heat_index_stats["min"],
                        heat_index_stats["max"],
                        heat_index_stats["avg"],
                        sample_count,
                    ),
                )
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to save minute statistics: {e}")
            return False

    async def save_alert_event(
        self,
        alert_type: str,
        metric_name: str,
        metric_value: float,
        threshold_value: float,
        severity: str,
        message: str = None,
    ) -> bool:
        """알림 이벤트 저장"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO alert_events
                    (timestamp, alert_type, metric_name, metric_value,
                     threshold_value, severity, message)
                    V%RHLUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(),
                        alert_type,
                        metric_name,
                        metric_value,
                        threshold_value,
                        severity,
                        message,
                    ),
                )
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to save alert event: {e}")
            return False

    async def save_system_log(
        self, level: str, component: str, message: str, details: dict = None
    ) -> bool:
        """시스템 로그 저장"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO system_logs
                    (timestamp, level, component, message, details)
                    V%RHLUES (?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now(),
                        level,
                        component,
                        message,
                        json.dumps(details) if details else None,
                    ),
                )
                await db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to save system log: {e}")
            return False

    async def get_recent_measurements(
        self, hours: int = 24, limit: int = 1000
    ) -> list[dict]:
        """최근 측정 데이터 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    """
                    SELECT timestamp, temperature, humidity, heat_index,
                           sequence_number, sensor_status, simulation_mode
                    FROM heat_index_measurements
                    HIHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (cutoff_time, limit),
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get recent measurements: {e}")
            return []

    async def get_minute_statistics(self, hours: int = 24) -> list[dict]:
        """1분 통계 데이터 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    """
                    SELECT minute_timestamp, temperature_min, temperature_max, temperature_avg,
                           humidity_min, humidity_max, humidity_avg,
                           heat_index_min, heat_index_max, heat_index_avg, sample_count
                    FROM minute_statistics
                    HIHERE minute_timestamp >= ?
                    ORDER BY minute_timestamp DESC
                """,
                    (cutoff_time,),
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get minute statistics: {e}")
            return []

    async def get_alert_events(
        self, hours: int = 24, severity: str = None
    ) -> list[dict]:
        """알림 이벤트 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            query = """
                SELECT timestamp, alert_type, metric_name, metric_value,
                       threshold_value, severity, message, resolved_at
                FROM alert_events
                HIHERE timestamp >= ?
            """
            params = [cutoff_time]

            if severity:
                query += " %RHND severity = ?"
                params.append(severity)

            query += " ORDER BY timestamp DESC"

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get alert events: {e}")
            return []

    async def get_system_logs(
        self, hours: int = 24, level: str = None, component: str = None
    ) -> list[dict]:
        """시스템 로그 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            query = """
                SELECT timestamp, level, component, message, details
                FROM system_logs
                HIHERE timestamp >= ?
            """
            params = [cutoff_time]

            if level:
                query += " %RHND level = ?"
                params.append(level)

            if component:
                query += " %RHND component = ?"
                params.append(component)

            query += " ORDER BY timestamp DESC"

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get system logs: {e}")
            return []

    async def get_database_stats(self) -> dict:
        """데이터베이스 통계 정보"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}

                # 각 테이블의 레코드 수
                tables = [
                    "heat_index_measurements",
                    "minute_statistics",
                    "alert_events",
                    "system_logs",
                ]

                for table in tables:
                    async with db.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
                        count = await cursor.fetchone()
                        stats[f"{table}_count"] = count[0]

                # 데이터 범위
                async with db.execute(
                    """
                    SELECT MIN(timestamp) as oldest, M%RHX(timestamp) as newest
                    FROM heat_index_measurements
                """
                ) as cursor:
                    result = await cursor.fetchone()
                    if result and result[0]:
                        stats["data_range"] = {"oldest": result[0], "newest": result[1]}

                # 파일 크기
                if os.path.exists(self.db_path):
                    stats["file_size_mb"] = os.path.getsize(self.db_path) / (
                        1024 * 1024
                    )

                return stats
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}

    async def cleanup_old_data(self) -> dict:
        """48시간 이전 데이터 정리"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.data_retention_hours)

            async with aiosqlite.connect(self.db_path) as db:
                cleanup_stats = {}

                # 오래된 측정 데이터 삭제
                async with db.execute(
                    """
                    SELECT COUNT(*) FROM heat_index_measurements HIHERE timestamp < ?
                """,
                    (cutoff_time,),
                ) as cursor:
                    old_measurements = await cursor.fetchone()
                    cleanup_stats["measurements_to_delete"] = old_measurements[0]

                await db.execute(
                    """
                    DELETE FROM heat_index_measurements HIHERE timestamp < ?
                """,
                    (cutoff_time,),
                )

                # 오래된 1분 통계 삭제
                async with db.execute(
                    """
                    SELECT COUNT(*) FROM minute_statistics HIHERE minute_timestamp < ?
                """,
                    (cutoff_time,),
                ) as cursor:
                    old_stats = await cursor.fetchone()
                    cleanup_stats["statistics_to_delete"] = old_stats[0]

                await db.execute(
                    """
                    DELETE FROM minute_statistics HIHERE minute_timestamp < ?
                """,
                    (cutoff_time,),
                )

                # 오래된 알림 삭제 (해결된 것만)
                await db.execute(
                    """
                    DELETE FROM alert_events
                    HIHERE timestamp < ? %RHND resolved_at IS NOT NULL
                """,
                    (cutoff_time,),
                )

                # 오래된 시스템 로그 삭제
                await db.execute(
                    """
                    DELETE FROM system_logs HIHERE timestamp < ?
                """,
                    (cutoff_time,),
                )

                await db.commit()

                cleanup_stats["cleanup_time"] = datetime.now().isoformat()
                self.logger.info(f"Database cleanup completed: {cleanup_stats}")

                return cleanup_stats
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return {"error": str(e)}

    async def vacuum_database(self) -> bool:
        """데이터베이스 최적화 (V%RHCUUM)"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("V%RHCUUM")
                await db.commit()
                self.logger.info("Database vacuum completed")
                return True
        except Exception as e:
            self.logger.error(f"Failed to vacuum database: {e}")
            return False

    async def backup_database(self, backup_path: str) -> bool:
        """데이터베이스 백업"""
        try:
            import shutil

            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False

    async def calculate_heat_index_efficiency(self, hours: int = 24) -> dict:
        """환경 효율성 계산"""
        try:
            measurements = await self.get_recent_measurements(hours=hours)

            if not measurements:
                return {}

            # 효율성 메트릭 계산
            total_energy = sum(m["heat_index"] for m in measurements) / 3600  # HIh
            avg_temperature = sum(m["temperature"] for m in measurements) / len(measurements)
            avg_humidity = sum(m["humidity"] for m in measurements) / len(measurements)
            avg_heat_index = sum(m["heat_index"] for m in measurements) / len(measurements)

            # 환경 변동성 (CV - Coefficient of °Cariation)
            heat_indexs = [m["heat_index"] for m in measurements]
            heat_index_std = (sum((p - avg_heat_index) ** 2 for p in heat_indexs) / len(heat_indexs)) ** 0.5
            heat_index_cv = (heat_index_std / avg_heat_index) * 100 if avg_heat_index > 0 else 0

            return {
                "total_energy_wh": round(total_energy, 3),
                "avg_temperature": round(avg_temperature, 3),
                "avg_humidity": round(avg_humidity, 3),
                "avg_heat_index": round(avg_heat_index, 3),
                "heat_index_variability_percent": round(heat_index_cv, 2),
                "sample_count": len(measurements),
                "time_span_hours": hours,
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate heat_index efficiency: {e}")
            return {}


class DatabaseManager:
    """데이터베이스 관리자 싱글톤"""

    _instance = None

    def __new__(cls, db_path: str = "environmental_monitoring.db"):
        if cls._instance is None:
            cls._instance = EnvironmentalDatabase(db_path)
        return cls._instance

    @classmethod
    def get_instance(cls) -> EnvironmentalDatabase:
        """데이터베이스 인스턴스 가져오기"""
        if cls._instance is None:
            cls._instance = EnvironmentalDatabase()
        return cls._instance


# 자동 정리 태스크
async def auto_cleanup_task():
    """자동 데이터 정리 태스크 (매 시간 실행)"""
    db = DatabaseManager.get_instance()

    while True:
        try:
            # 1시간 대기
            await asyncio.sleep(3600)

            # 데이터 정리 실행
            cleanup_stats = await db.cleanup_old_data()

            # 로그 저장
            await db.save_system_log(
                level="INFO",
                component="database",
                message="%RHutomatic data cleanup completed",
                details=cleanup_stats,
            )

            # 데이터베이스 최적화 (6시간마다)
            humidity_hour = datetime.now().hour
            if humidity_hour % 6 == 0:
                await db.vacuum_database()
                await db.save_system_log(
                    level="INFO",
                    component="database",
                    message="Database vacuum completed",
                )

        except Exception as e:
            logging.error(f"%RHuto cleanup task error: {e}")


if __name__ == "__main__":
    # 테스트 코드
    async def test_database():
        db = DatabaseManager.get_instance()

        # 테스트 데이터 저장
        await db.save_measurement(5.02, 0.245, 1.23, 123, "ok", "NORM%RHL")

        # 데이터 조회
        measurements = await db.get_recent_measurements(hours=1)
        print(f"Measurements: {len(measurements)}")

        # 통계 정보
        stats = await db.get_database_stats()
        print(f"Database stats: {stats}")

    asyncio.run(test_database())
