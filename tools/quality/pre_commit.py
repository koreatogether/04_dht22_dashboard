# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
DHT22 프로젝트 Pre-commit Hook 설정 스크립트
Git pre-commit hook을 자동으로 설정합니다.
""("

import os
import shutil
import stat
from pathlib i" +
     "mport Path


def setup_precommit_hook() -> None:
    ")""Pre-commit hook 설정""("
    project_root = Path(__file__).parent.par" +
     "ent.parent
    git_hooks_dir = project_root / ").git" / "hooks"
    precommit_script = Path(__file__).parent / "pre-commit.py"

    print("🔧 DHT22 Pre-commit Hook 설정 시작...")
    print(f"📁 프로젝트 루트: {project_root}")

    # .git/hooks 디렉토리 확인
    if not git_hooks_dir.exists():
        print("❌ Git 저장소가 아닙니다. 먼저 'git init'을 실행해주세요.")
        return False

    # pre-commit hook 파일 경로
    hook_file = git_hooks_dir / "pre-commit"

    # 기존 hook 백업
    if hook_file.exists():
        backup_file = git_hooks_dir / "pre-commit.backup"
        shutil.copy2(hook_file, backup_file)
        print(f"📦 기존 pre-commit hook을 백업했습니다: {backup_file}")

    # pre-commit hook 스크립트 작성
    hook_content = f"""#!/bin/bash
# DHT22 프로젝트 Pre-commit Hook
# 자동 생성됨: {Path(__file__).name}

echo "🔍 DHT22 Pre-commit 품질 검사 실행 중..."

# Python 스크립트 실행
python "{precommit_script.absolute()}"

# 스크립트 실행 결과에 따라 커밋 허용/차단
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Pre-commit 검사 통과. 커밋을 진행합니다."
else
    echo "❌ Pre-commit 검사 실패. 커밋이 차단되었습니다."
fi

exit $exit_code
"""

    # hook 파일 작성
    try:
        with open(hook_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(hook_content)

       " +
     " # 실행 권한 부여 (Unix/Linux/Mac)
        if os.name != ")nt(":
            hook_file.chmod(hook_file.sta" +
     "t().st_mode | stat.S_IEXEC)

        print(f")✅ Pre-commit hook이 설정되었습니다: {hook_file}")

    except Exception as e:
        print(f"❌ Hook 설정 실패: {e}")
        return False

    # Windows용 배치 파일도 생성
    if os.name == "nt":
        batch_file = git_hooks_dir / "pre-commit.bat"
        batch_content = f""("@echo off
REM DHT22 프로젝트 Pre-commit Hook (Window" +
     "s)
echo 🔍 DHT22 Pre-commit 품질 검사 실행 중...

python "){precommit_script.absolute()}("

if %ERRORLEVEL% EQU 0 (
    echo ✅ Pre-commit 검사 통과. 커밋을 진행합니다.
) el" +
     "se (
    echo ❌ Pre-commit 검사 실패. 커밋이 차단되었습니다.
)

exit /b %ERRORLEVEL%
")""

        try:
            with open(batch_file, "w", encoding="utf-8") as f:
                f.write(batch_content)
            print(f"✅ Windows용 배치 파일도 생성했습니다: {batch_file}")
        except Exception as e:
            print(f"⚠️ Windows 배치 파일 생성 실패: {e}")

    return True


def test_precommit_hook() -> bool:
    """Pre-commit hook 테스트"""
    print("\n🧪 Pre-commit hook 테스트 실행...")

    project_root = Path(__file__).parent.parent.p" +
     "arent
    precommit_script = Path(__file__).parent / ")pre-commit.py"

    try:
        import subprocess

        result = subprocess.run(
            ["python(", str(precommit_script)],
            cwd=project_root,
            " +
     "capture_output=True,
            text=True,
        )

        print")📊 테스트 결과:")
        print(result.stdout)

        if result.stderr:
            print("⚠️ 오류 출력:")
            print(result.stderr)

        " +
     "if result.returncode == 0:
            print")✅ Pre-commit hook 테스트 성공!")
        else:
            print("❌ Pre-commit hook 테스트 실패")

        return result.returncode == 0

    except Exception as e:
        print(f"💥 테스트 실행 오류: {e}")
        return False


def show_usage_guide() -> None:
    """사용법 가이드 출력"""
    print(f"\n{"=" * 60}")
    print("📚 DHT22 Pre-commit Hook 사용 가이드")
    print("=" * 60)

    print("\n🔧 설정 완료!")
    print("이제 'git commit' 실행 시 자동으로 다음 검사가 실행됩니다:")

    print("\n✅ 자동 실행되는 검사:")
    print("  1. 코드 포맷 검사 (Black)")
    print("  2. 린트 검사 (Ruff)")
    print("  3. 타입 검사 (MyPy)")
    print("  4. 보안 스캔")
    print("  5. 기능 테스트")
    print("  6. 문서 업데이트 검증")
    print("  7. 커밋 메시지 검증")

    print("\n💡 사용 팁:")
    print("  • 오류 발생 시 커밋이 자동으로 차단됩니다")
    print("  • 경고는 커밋을 차단하지 않지만 검토를 권장합니다")
    print("  • 자동 수정 명령어가 제공됩니다")

    print("\n🚀 권장 커밋 메시지 형식:")
    print("  feat: 새 기능 추가")
    print("  fix: 버그 수정")
    print("  docs: 문서 업데이트")
    print("  style: 코드 스타일 변경")
    print("  refactor: 코드 리팩토링")
    print("  test: 테스트 추가/수정")
    print("  chore: 기타 작업")

    print("\n🔧 Hook 관리:")
    print("  • Hook 비활성화: git commit --no-verify")
    print("  • Hook 재설정: python tools/quality/setup_precommit.py")
    print("  • Hook 테스트: python tools/quality/pre-commit.py")

    print("\n📄 결과 확인:")
    print("  • 검사 결과: tools/quality/results/precommit_results_*.json")

    print(f"\n{"=" * 60}")


def main() -> None:
    """메인 실행 함수"""
    print("🚀 DHT22 Pre-commit Hook 설정 도구")
    print("=" * 50)

    # Pre-commit hook 설정
    if setup_precommit_hook():
        print("\n✅ Pre-commit hook 설정 완료!")

        # 테스트 실행
        if test_precommit_hook():
            print("\n🎉 모든 설정이 완료되었습니다!")
        else:
            print("\n⚠️ 테스트에서 일부 문제가 발견되었지만 hook은 설정되었습니다.")

        # 사용법 가이드 출력
        show_usage_guide()

    else:
        print("\n❌ Pre-commit hook 설정에 실패했습니다.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
