# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
MyPy 타입 힌트 오류 일괄 수정 스크립트 - 3차
나머지 함수들과 변수들의 타입 힌트 완성
"""

# Windows UTF-8 콘솔 지원
import io
import sys
if sys.platform == "win32":
    import os
    os.system("chcp 65001 > nul")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

import re
from pathlib import Path

def apply_final_type_fixes() -> int:
    """최종 타입 힌트 수정 적용"""
    
    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("❌ tools 디렉토리를 찾을 수 없습니다.")
        return 0
    
    fixed_count = 0
    
    # 모든 Python 파일에 대해 일괄 수정
    for py_file in tools_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            original_content = content
            
            # 1. 매개변수 없는 함수들의 반환 타입 지정
            patterns_to_fix = [
                # 매개변수 없는 함수들 - bool 반환
                (r'^(\s*)def (check|verify|validate|test)_[a-zA-Z_]+\(\):\s*$', r'\1def \2_\3() -> bool:'),
                (r'^(\s*)def is_[a-zA-Z_]+\(\):\s*$', r'\1def is_\2() -> bool:'),
                (r'^(\s*)def has_[a-zA-Z_]+\(\):\s*$', r'\1def has_\2() -> bool:'),
                
                # 매개변수 없는 함수들 - None 반환  
                (r'^(\s*)def (setup|init|configure|install)_[a-zA-Z_]+\(\):\s*$', r'\1def \2_\3() -> None:'),
                (r'^(\s*)def (show|print|display)_[a-zA-Z_]+\(\):\s*$', r'\1def \2_\3() -> None:'),
                (r'^(\s*)def (run|execute|start)_[a-zA-Z_]+\(\):\s*$', r'\1def \2_\3() -> None:'),
                
                # 매개변수 없는 함수들 - 기타
                (r'^(\s*)def get_[a-zA-Z_]+\(\):\s*$', r'\1def get_\2() -> dict:'),
                (r'^(\s*)def load_[a-zA-Z_]+\(\):\s*$', r'\1def load_\2() -> dict:'),
                (r'^(\s*)def generate_[a-zA-Z_]+\(\):\s*$', r'\1def generate_\2() -> str:'),
                
                # 매개변수가 있는 함수들 타입 힌트 추가
                (r'^(\s*)def ([a-zA-Z_]+)\(([^)]*[^:])\):\s*$', r'\1def \2(\3) -> None:'),
            ]
            
            for pattern, replacement in patterns_to_fix:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    content = new_content
                    print(f"  🔧 패턴 수정 적용: {py_file.name}")
                    
            # 2. import 구문에 typing 추가 (필요한 경우)
            if "def " in content and "-> " in content and "from typing import" not in content:
                # 파일 상단에 typing import 추가
                if content.startswith("#!/usr/bin/env python3"):
                    lines = content.split('\n')
                    insert_pos = 1
                    # docstring이 있으면 그 다음에 삽입
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip().startswith('"""') and line.strip().endswith('"""'):
                            insert_pos = i + 1
                            break
                        elif line.strip().startswith('"""'):
                            # 여러 줄 docstring 찾기
                            for j in range(i + 1, len(lines)):
                                if lines[j].strip().endswith('"""'):
                                    insert_pos = j + 1
                                    break
                            break
                        elif line.strip() and not line.startswith('#'):
                            break
                    
                    # typing import가 이미 있는지 확인
                    has_typing_import = any("from typing import" in line or "import typing" in line for line in lines)
                    if not has_typing_import:
                        lines.insert(insert_pos, "from typing import Optional, Any")
                        lines.insert(insert_pos + 1, "")
                        content = '\n'.join(lines)
                        print(f"  📝 typing import 추가: {py_file.name}")
            
            # 변경사항이 있으면 파일 저장
            if content != original_content:
                py_file.write_text(content, encoding='utf-8')
                fixed_count += 1
                print(f"✅ 수정완료: {py_file}")
                        
        except Exception as e:
            print(f"❌ 오류 발생 {py_file}: {e}")
            continue
    
    return fixed_count

if __name__ == "__main__":
    print("🔧 MyPy 타입 힌트 3차 최종 수정 시작...")
    
    fixed = apply_final_type_fixes()
    print(f"\n✅ 총 {fixed}개 파일 수정 완료!")
    
    if fixed > 0:
        print("🧪 MyPy 검사로 결과 확인 중...")
        import subprocess
        import sys
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "mypy", "tools/", 
                "--ignore-missing-imports"
            ], capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                errors = result.stdout.count("error:")
                print(f"📊 남은 MyPy 오류: {errors}개")
                
                if errors > 0:
                    print("\n🎯 주요 남은 오류들:")
                    lines = result.stdout.split('\n')
                    error_lines = [line for line in lines if "error:" in line][:5]
                    for error_line in error_lines:
                        print(f"   {error_line}")
            else:
                print("✅ MyPy 오류 없음!")
                
        except Exception as e:
            print(f"⚠️ MyPy 검사 실패: {e}")
    
    print("🏁 3차 최종 수정 완료!")