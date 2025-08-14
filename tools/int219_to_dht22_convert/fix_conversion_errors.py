#!/usr/bin/env python3
"""변환 오류 수정 스크립트"""

import re
from pathlib import Path

def fix_conversion_errors():
    """변환 과정에서 발생한 오류들을 수정"""
    print("🔧 변환 오류 수정 중...")
    
    # 수정할 패턴들
    fixes = [
        (r'°CalueError', 'ValueError'),
        (r'%RHttributeError', 'AttributeError'),
        (r'°C\b(?![\w°])', 'V'),  # 단독으로 사용된 °C를 V로 복원
        (r'%RH\b(?![\w%])', 'A'),  # 단독으로 사용된 %RH를 A로 복원
        (r'HI\b(?![a-zA-Z])', 'W'),  # 단독으로 사용된 HI를 W로 복원
        (r'temperature_range.*=.*\[.*\]', 'voltage_range = [4.0, 6.0]'),
        (r'humidity_range.*=.*\[.*\]', 'current_range = [0.0, 1.0]'),
    ]
    
    fixed_count = 0
    
    # src 디렉토리의 Python 파일들만 수정
    for file_path in Path("src").rglob("*.py"):
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # 각 패턴 적용
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content)
            
            # 변경사항이 있으면 저장
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                fixed_count += 1
                print(f"  ✅ 수정됨: {file_path}")
                
        except Exception as e:
            print(f"  ⚠️ 수정 실패: {file_path} - {e}")
    
    print(f"✅ {fixed_count}개 파일 수정 완료")

if __name__ == "__main__":
    fix_conversion_errors()
    print("\n🎉 변환 오류 수정이 완료되었습니다!")
    print("다음 단계: python src/python/backend/main.py 로 서버 실행")