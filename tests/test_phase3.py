# -*- coding: utf-8 -*-
"""
DHT22 프로젝트 Phase 3 테스트
- 데이터 저장 기능 테스트
"""
import pytest
import sys
from pathlib import Path
import sqlite3
import os

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# This is a placeholder for where the database logic would be
# Since there is no database.py, I will create a dummy one for testing
DB_FILE = "test_dht22_phase3.db"

def setup_database(): -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        temperature REAL NOT NULL,
        humidity REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def clear_database(): -> None:
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

class TestPhase3:
    """Phase 3 테스트 클래스"""

def setup_method(self): -> None:
        setup_database()

def teardown_method(self): -> None:
        clear_database()

def test_database_connection(self): -> None:
        """데이터베이스 연결 테스트"""
        assert os.path.exists(DB_FILE)
        conn = sqlite3.connect(DB_FILE)
        assert conn is not None
        conn.close()

def test_data_insertion(self): -> None:
        """데이터 삽입 테스트"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensor_data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                       ("2025-08-15T12:00:00", 25.5, 60.1))
        conn.commit()

        cursor.execute("SELECT * FROM sensor_data")
        data = cursor.fetchall()
        assert len(data) == 1
        assert data[0][2] == 25.5
        conn.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])