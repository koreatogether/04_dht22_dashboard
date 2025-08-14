# DHT22 프로젝트 임시 파일 저장소

이 폴더는 DHT22 프로젝트 개발 과정에서 현재 사용하지 않는 파일들을 임시로 보관하는 곳입니다.

## 📁 보관된 파일들

### backend/ - INA219에서 변환된 백엔드 파일들
- `main.py` - INA219 원본 메인 서버 (변환된 파일)
- `main_backup.py` - INA219 백업 서버
- `data_analyzer.py` - INA219 데이터 분석 모듈
- `database.py` - INA219 데이터베이스 관리 모듈
- `test_ai_self_phase2_3.py` - INA219 테스트 파일

### 삭제된 파일들 (불필요한 파일들)
- `test_phase*.py` - INA219 관련 테스트 파일들 (7개)
- `power_monitoring.db` - INA219 데이터베이스 파일
- `test_power_monitoring.db` - INA219 테스트 데이터베이스
- `test_websocket.html` - 테스트용 HTML 파일
- `server.log` - 이전 로그 파일
- `requirements*.txt` - 중복된 의존성 파일들 (2개)
- `README.md` - 백엔드 폴더의 중복 README
- `simulator/` 폴더 전체 - INA219 시뮬레이터 파일들 (5개)

### 현재 사용 중인 핵심 파일들 (src/python/backend/)
- ✅ `dht22_dev_server.py` - DHT22 개발 서버 (메인)
- ✅ `dht22_main.py` - DHT22 기본 서버
- ✅ `climate_calculator.py` - DHT22 환경 계산 유틸리티

## 🗂️ 파일 정리 일시
- **정리 일시**: 2025-08-14
- **정리 사유**: DHT22 프로젝트 구조 정리 및 최적화
- **보관 기간**: 프로젝트 완료 후 검토

---
**정리자**: Kiro AI Assistant  
**프로젝트**: DHT22 환경 모니터링 시스템