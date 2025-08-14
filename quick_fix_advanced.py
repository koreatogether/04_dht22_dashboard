#!/usr/bin/env python3
"""
고급 자동 수정 도구 - AI 코딩 문제 패턴 학습 기반
수동으로 수정했던 모든 패턴을 자동화
"""

# Windows UTF-8 콘솔 지원
import io
import sys

if sys.platform == "win32":
    import os

    os.system("chcp 65001 > nul")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

import re
import subprocess
from datetime import datetime
from pathlib import Path


class AdvancedCodeFixer:
    """AI 코딩 문제 패턴 학습 기반 고급 자동 수정"""

def __init__(self): -> None:
        self.project_root = Path.cwd()
        self.backup_dir = (
            self.project_root / "tools" / "quality" / "backups" / "advanced"
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 수동 수정했던 모든 패턴들을 학습하여 자동화
        self.fix_patterns = {
            # 1. 타입 힌트 고급 패턴
            "advanced_type_hints": [
                # 복잡한 함수 시그니처들
                (
                    r"def ([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\):\s*$",
                    self._fix_function_signature,
                ),
                (
                    r"async def ([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\):\s*$",
                    self._fix_async_function_signature,
                ),
                # 클래스 생성자
                (r"def __init__\(self([^)]*)\):\s*$", r"def __init__(self\1) -> None:"),
                # 매직 메서드들
                (r"def __str__\(self\):\s*$", r"def __str__(self) -> str:"),
                (r"def __repr__\(self\):\s*$", r"def __repr__(self) -> str:"),
                (r"def __len__\(self\):\s*$", r"def __len__(self) -> int:"),
                (r"def __bool__\(self\):\s*$", r"def __bool__(self) -> bool:"),
            ],
            # 2. FastAPI/WebSocket 특화 패턴
            "fastapi_patterns": [
                # WebSocket 핸들러들
                (
                    r"async def websocket_endpoint\(websocket: WebSocket\):\s*$",
                    r"async def websocket_endpoint(websocket: WebSocket) -> None:",
                ),
                (
                    r"async def connect\(self, websocket: WebSocket\):\s*$",
                    r"async def connect(self, websocket: WebSocket) -> None:",
                ),
                (
                    r"async def disconnect\(self, websocket: WebSocket\):\s*$",
                    r"async def disconnect(self, websocket: WebSocket) -> None:",
                ),
                (
                    r"async def broadcast\(self, message: str\):\s*$",
                    r"async def broadcast(self, message: str) -> None:",
                ),
                # API 엔드포인트들
                (r"async def root\(\):\s*$", r"async def root() -> HTMLResponse:"),
                (
                    r"async def get_current_data\(\):\s*$",
                    r"async def get_current_data() -> dict:",
                ),
                (
                    r"async def get_metrics\(\):\s*$",
                    r"async def get_metrics() -> dict:",
                ),
                (
                    r"async def health_check\(\):\s*$",
                    r"async def health_check() -> dict:",
                ),
            ],
            # 3. 변수 어노테이션 패턴
            "variable_annotations": [
                # 클래스 변수들
                (r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = \[\]", r"\1\2: list = []"),
                (r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = \{\}", r"\1\2: dict = {}"),
                (r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = set\(\)", r"\1\2: set = set()"),
                (r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = ""', r'\1\2: str = ""'),
                (r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = 0", r"\1\2: int = 0"),
                (r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = False", r"\1\2: bool = False"),
                (r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = True", r"\1\2: bool = True"),
                (
                    r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = None",
                    r"\1\2: Optional[Any] = None",
                ),
            ],
            # 4. Import 문제 해결
            "import_fixes": [
                # 불필요한 typing imports 제거
                (r"from typing import Dict, List, Set, Tuple\n", ""),
                (r"from typing import Dict, List, Set\n", ""),
                (r"from typing import Dict, List\n", ""),
                (r"from typing import List, Dict\n", ""),
                # 현대적 타입으로 변환
                (r"-> Dict\[", r"-> dict["),
                (r"-> List\[", r"-> list["),
                (r"-> Set\[", r"-> set["),
                (r"-> Tuple\[", r"-> tuple["),
                (r": Dict\[", r": dict["),
                (r": List\[", r": list["),
                (r": Set\[", r": set["),
                (r": Tuple\[", r": tuple["),
                # Optional import 추가
                (r"(from typing import [^\n]*)", self._ensure_optional_import),
            ],
            # 5. 라인 길이 자동 분할
            "line_length_fixes": [
                # 긴 함수 호출 분할
                (
                    r"([a-zA-Z_][a-zA-Z0-9_]*\([^)]{80,}\))",
                    self._split_long_function_call,
                ),
                # 긴 문자열 분할
                (r'("[^"]{80,}")', self._split_long_string),
                # 긴 딕셔너리/리스트 분할
                (r"(\{[^}]{80,}\})", self._split_long_dict),
                (r"(\[[^\]]{80,}\])", self._split_long_list),
            ],
            # 6. 일반적인 코드 문제들
            "common_issues": [
                # 예외 처리 개선
                (r"except Exception:", r"except Exception as e:"),
                (
                    r"except (ValueError|TypeError|AttributeError):",
                    r"except (\1) as e:",
                ),
                # f-string 개선
                (r'print\("([^"]*)" \+ ([^)]+)\)', r'print(f"\1{\2}")'),
                # 비교 연산자 개선
                (r" == True", r" is True"),
                (r" == False", r" is False"),
                (r" == None", r" is None"),
                (r" != None", r" is not None"),
            ],
        }

        self.fixes_applied = []
        self.files_modified = []

def _fix_function_signature(self, match): -> None:
        """함수 시그니처 자동 수정"""
        func_name = match.group(1)
        params = match.group(2)

        # 반환 타입 추론
        if func_name.startswith(("get_", "fetch_", "load_")):
            return_type = "dict"
        elif func_name.startswith(("is_", "has_", "can_", "should_")):
            return_type = "bool"
        elif func_name.startswith(("create_", "generate_", "build_")):
            return_type = "str"
        elif func_name in ["main", "run", "start", "stop", "setup", "cleanup"]:
            return_type = "None"
        else:
            return_type = "None"  # 기본값

        return f"def {func_name}({params}) -> {return_type}:"

def _fix_async_function_signature(self, match): -> None:
        """비동기 함수 시그니처 자동 수정"""
        func_name = match.group(1)
        params = match.group(2)

        # FastAPI 엔드포인트 패턴
        if func_name == "root":
            return_type = "HTMLResponse"
        elif func_name.startswith("get_"):
            return_type = "dict"
        elif func_name in ["connect", "disconnect", "broadcast"]:
            return_type = "None"
        else:
            return_type = "None"

        return f"async def {func_name}({params}) -> {return_type}:"

def _ensure_optional_import(self, match): -> None:
        """Optional import가 필요하면 추가"""
        import_line = match.group(1)
        if "Optional" not in import_line and "Any" not in import_line:
            return import_line + ", Optional, Any"
        elif "Optional" not in import_line:
            return import_line + ", Optional"
        elif "Any" not in import_line:
            return import_line + ", Any"
        return import_line

def _split_long_function_call(self, match): -> None:
        """긴 함수 호출을 여러 줄로 분할"""
        call = match.group(1)
        if len(call) > 88:  # ruff 기본 라인 길이
            # 간단한 분할 로직
            parts = call.split(", ")
            if len(parts) > 1:
                return "(\n        " + ",\n        ".join(parts) + "\n    )"
        return call

def _split_long_string(self, match): -> None:
        """긴 문자열을 여러 줄로 분할"""
        string = match.group(1)
        if len(string) > 88:
            # 간단한 분할 - 중간지점에서 분할
            mid = len(string) // 2
            return f'("{string[1:mid]}" +\n     "{string[mid:-1]}")'
        return string

def _split_long_dict(self, match): -> None:
        """긴 딕셔너리를 여러 줄로 분할"""
        dict_str = match.group(1)
        if len(dict_str) > 88:
            return (
                "{\n        " + dict_str[1:-1].replace(", ", ",\n        ") + "\n    }"
            )
        return dict_str

def _split_long_list(self, match): -> None:
        """긴 리스트를 여러 줄로 분할"""
        list_str = match.group(1)
        if len(list_str) > 88:
            return (
                "[\n        " + list_str[1:-1].replace(", ", ",\n        ") + "\n    ]"
            )
        return list_str

    def apply_fixes_to_file(self, file_path: Path) -> int:
        """파일에 모든 수정 패턴 적용"""
        if not file_path.suffix == ".py":
            return 0

        print(f"🔧 고급 수정 적용: {file_path.name}")

        # 백업 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{file_path.name}_{timestamp}.bak"
        backup_file.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")

        content = file_path.read_text(encoding="utf-8")
        original_content = content
        fixes_count = 0

        # 모든 패턴 카테고리 적용
        for category_name, patterns in self.fix_patterns.items():
            print(f"  📋 {category_name} 패턴 적용 중...")

            for pattern, replacement in patterns:
                if callable(replacement):
                    # 함수 기반 치환
                    new_content = re.sub(
                        pattern, replacement, content, flags=re.MULTILINE
                    )
                else:
                    # 문자열 기반 치환
                    new_content = re.sub(
                        pattern, replacement, content, flags=re.MULTILINE
                    )

                if new_content != content:
                    matches = len(re.findall(pattern, content, flags=re.MULTILINE))
                    fixes_count += matches
                    content = new_content
                    print(f"    ✅ {matches}개 수정: {pattern[:50]}...")

        # 변경사항 저장
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            self.files_modified.append(file_path)
            self.fixes_applied.append(
                {
                    "file": str(file_path),
                    "fixes_count": fixes_count,
                    "backup": str(backup_file),
                }
            )

        return fixes_count

def run_advanced_fixes(self): -> None:
        """고급 자동 수정 실행"""
        print("🚀 고급 자동 수정 도구 시작...")
        print("=" * 60)

        # Python 파일들 찾기
        python_files = []
        for pattern in ["src/**/*.py", "tools/**/*.py", "tests/**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))

        print(f"📁 발견된 Python 파일: {len(python_files)}개")

        total_fixes = 0
        for py_file in python_files:
            try:
                fixes = self.apply_fixes_to_file(py_file)
                total_fixes += fixes
            except Exception as e:
                print(f"❌ 오류 발생 {py_file}: {e}")

        print("\n" + "=" * 60)
        print("✅ 고급 자동 수정 완료!")
        print(f"📊 수정된 파일: {len(self.files_modified)}개")
        print(f"🔧 총 수정사항: {total_fixes}개")
        print(f"💾 백업 위치: {self.backup_dir}")

        # 수정 결과 검증
        self._verify_fixes()

        return len(self.files_modified), total_fixes

def _verify_fixes(self): -> None:
        """수정 결과 검증"""
        print("\n🧪 수정 결과 검증 중...")

        try:
            # Ruff 검사
            ruff_result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "src/", "tools/", "tests/"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            ruff_errors = ruff_result.stdout.count("error") if ruff_result.stdout else 0
            print(f"  🔍 Ruff 오류: {ruff_errors}개")

            # MyPy 검사
            mypy_result = subprocess.run(
                [sys.executable, "-m", "mypy", "tools/", "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            mypy_errors = (
                mypy_result.stdout.count("error:") if mypy_result.stdout else 0
            )
            print(f"  🎯 MyPy 오류: {mypy_errors}개")

        except Exception as e:
            print(f"  ⚠️ 검증 실패: {e}")


def main(): -> None:
    """메인 실행"""
    try:
        fixer = AdvancedCodeFixer()
        fixer.run_advanced_fixes()
        print("\n🎉 모든 자동 수정이 완료되었습니다!")

    except KeyboardInterrupt:
        print("\n🛑 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")


if __name__ == "__main__":
    main()
