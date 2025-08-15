#!/usr/bin/env python3
"""
환경변수 로더 테스트

env_loader.py의 기능을 테스트합니다.
"""

import os

# 테스트 대상 모듈 import
import sys
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from utils.env_loader import (
    EnvLoader,
    get_bool,
    get_float,
    get_int,
    get_list,
    get_str,
    load_database_config,
    load_logging_config,
    load_sensor_config,
    load_server_config,
)


class TestEnvLoader:
    """EnvLoader 클래스 테스트"""

    def test_init_with_default_env_file(self):
        """기본 .env 파일 경로로 초기화 테스트"""
        loader = EnvLoader()
        assert loader.env_file.name == ".env"

    def test_init_with_custom_env_file(self):
        """커스텀 .env 파일 경로로 초기화 테스트"""
        custom_path = "/custom/.env"
        loader = EnvLoader(custom_path)
        # Windows path normalization
        expected_path = custom_path.replace('/', '\\')
        assert str(loader.env_file) == expected_path

    @patch("builtins.open", mock_open(read_data="TEST_VAR=test_value\n# Comment\nEMPTY_LINE=\n"))
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_env_file_success(self, mock_exists):
        """환경변수 파일 로드 성공 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            EnvLoader()
            assert os.environ.get("TEST_VAR") == "test_value"

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_env_file_not_found(self, mock_exists, capsys):
        """환경변수 파일이 없을 때 테스트"""
        EnvLoader()
        captured = capsys.readouterr()
        assert ".env 파일을 찾을 수 없습니다" in captured.out

    @patch("builtins.open", mock_open(read_data='QUOTED_VAR="quoted value"\nSINGLE_QUOTED=\'single value\''))
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_env_file_with_quotes(self, mock_exists):
        """따옴표가 있는 환경변수 로드 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            EnvLoader()
            assert os.environ.get("QUOTED_VAR") == "quoted value"
            assert os.environ.get("SINGLE_QUOTED") == "single value"


class TestEnvGetters:
    """환경변수 getter 함수들 테스트"""

    def test_get_str_with_value(self):
        """문자열 환경변수 가져오기 테스트"""
        with patch.dict(os.environ, {"TEST_STR": "hello world"}):
            result = get_str("TEST_STR", "default")
            assert result == "hello world"

    def test_get_str_with_default(self):
        """문자열 환경변수 기본값 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            result = get_str("NONEXISTENT", "default_value")
            assert result == "default_value"

    def test_get_int_with_value(self):
        """정수 환경변수 가져오기 테스트"""
        with patch.dict(os.environ, {"TEST_INT": "42"}):
            result = get_int("TEST_INT", 0)
            assert result == 42

    def test_get_int_with_invalid_value(self):
        """잘못된 정수 환경변수 테스트"""
        with patch.dict(os.environ, {"TEST_INT": "not_a_number"}):
            result = get_int("TEST_INT", 100)
            assert result == 100  # 기본값 반환

    def test_get_float_with_value(self):
        """실수 환경변수 가져오기 테스트"""
        with patch.dict(os.environ, {"TEST_FLOAT": "3.14"}):
            result = get_float("TEST_FLOAT", 0.0)
            assert result == 3.14

    def test_get_float_with_invalid_value(self):
        """잘못된 실수 환경변수 테스트"""
        with patch.dict(os.environ, {"TEST_FLOAT": "not_a_float"}):
            result = get_float("TEST_FLOAT", 2.71)
            assert result == 2.71  # 기본값 반환

    def test_get_bool_true_values(self):
        """불린 환경변수 True 값들 테스트"""
        true_values = ["true", "1", "yes", "on", "TRUE", "YES"]
        for value in true_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                result = get_bool("TEST_BOOL", False)
                assert result is True, f"'{value}' should be True"

    def test_get_bool_false_values(self):
        """불린 환경변수 False 값들 테스트"""
        false_values = ["false", "0", "no", "off", "FALSE", "NO"]
        for value in false_values:
            with patch.dict(os.environ, {"TEST_BOOL": value}):
                result = get_bool("TEST_BOOL", True)
                assert result is False, f"'{value}' should be False"

    def test_get_bool_with_default(self):
        """불린 환경변수 기본값 테스트"""
        with patch.dict(os.environ, {"TEST_BOOL": "invalid"}):
            result = get_bool("TEST_BOOL", True)
            assert result is True  # 기본값 반환

    def test_get_list_with_value(self):
        """리스트 환경변수 가져오기 테스트"""
        with patch.dict(os.environ, {"TEST_LIST": "item1,item2,item3"}):
            result = get_list("TEST_LIST", ",", [])
            assert result == ["item1", "item2", "item3"]

    def test_get_list_with_custom_separator(self):
        """커스텀 구분자 리스트 환경변수 테스트"""
        with patch.dict(os.environ, {"TEST_LIST": "item1;item2;item3"}):
            result = get_list("TEST_LIST", ";", [])
            assert result == ["item1", "item2", "item3"]

    def test_get_list_with_empty_value(self):
        """빈 리스트 환경변수 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            result = get_list("NONEXISTENT", ",", ["default"])
            assert result == ["default"]


class TestConfigLoaders:
    """설정 로더 함수들 테스트"""

    def test_load_database_config(self):
        """데이터베이스 설정 로드 테스트"""
        env_vars = {
            "DB_HOST": "test_host",
            "DB_PORT": "5433",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_pass"
        }

        with patch.dict(os.environ, env_vars):
            config = load_database_config()

            assert config["host"] == "test_host"
            assert config["port"] == 5433
            assert config["database"] == "test_db"
            assert config["user"] == "test_user"
            assert config["password"] == "test_pass"

    def test_load_database_config_defaults(self):
        """데이터베이스 설정 기본값 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            config = load_database_config()

            assert config["host"] == "localhost"
            assert config["port"] == 5432
            assert config["database"] == "dht22_monitoring"
            assert config["user"] == "postgres"
            assert config["password"] == ""

    def test_load_server_config(self):
        """서버 설정 로드 테스트"""
        env_vars = {
            "HOST": "0.0.0.0",
            "PORT": "8080",
            "DEBUG": "true",
            "WS_HOST": "ws_host",
            "WS_PORT": "8081"
        }

        with patch.dict(os.environ, env_vars):
            config = load_server_config()

            assert config["host"] == "0.0.0.0"
            assert config["port"] == 8080
            assert config["debug"] is True
            assert config["ws_host"] == "ws_host"
            assert config["ws_port"] == 8081

    def test_load_sensor_config(self):
        """센서 설정 로드 테스트"""
        env_vars = {
            "SENSOR_PIN": "3",
            "SENSOR_TYPE": "DHT11",
            "SERIAL_PORT": "COM4",
            "BAUD_RATE": "115200"
        }

        with patch.dict(os.environ, env_vars):
            config = load_sensor_config()

            assert config["pin"] == 3
            assert config["type"] == "DHT11"
            assert config["serial_port"] == "COM4"
            assert config["baud_rate"] == 115200

    def test_load_logging_config(self):
        """로깅 설정 로드 테스트"""
        env_vars = {
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE_PATH": "custom/log/path.log"
        }

        with patch.dict(os.environ, env_vars):
            config = load_logging_config()

            assert config["level"] == "DEBUG"
            assert config["file_path"] == "custom/log/path.log"


@pytest.fixture
def temp_env_file():
    """임시 .env 파일 픽스처"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("TEST_VAR=test_value\n")
        f.write("# This is a comment\n")
        f.write("NUMERIC_VAR=123\n")
        f.write('QUOTED_VAR="quoted value"\n')
        temp_path = f.name

    yield temp_path

    # 정리
    os.unlink(temp_path)


def test_env_loader_with_real_file(temp_env_file):
    """실제 파일을 사용한 환경변수 로더 테스트"""
    with patch.dict(os.environ, {}, clear=True):
        EnvLoader(temp_env_file)

        assert os.environ.get("TEST_VAR") == "test_value"
        assert os.environ.get("NUMERIC_VAR") == "123"
        assert os.environ.get("QUOTED_VAR") == "quoted value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
