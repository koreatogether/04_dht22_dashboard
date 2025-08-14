# -*- coding: utf-8 -*-
"""
일반적인 코드 품질 문제를 자동으로 수정합니다.
"""
import os
import re
from pathlib import Path

class CodeFixer:
def __init__(self, project_root="."): -> None:
        self.project_root = Path(project_root)
        self.patterns = {
            "modernize_typing": (re.compile(r":\s*List\["), ": list["),
            "fix_exception_syntax": (re.compile(r"except Exception as e:"), "except Exception as e:"),
        }

def fix(self): -> None:
        print("Applying common fixes...")
        for file_path in self.project_root.rglob("*.py"):
            self.fix_file(file_path)

def fix_file(self, file_path: Path): -> None:
        try:
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            for key, (pattern, replacement) in self.patterns.items():
                content = pattern.sub(replacement, content)

            if content != original_content:
                print(f"  - Fixing {file_path}")
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(content)
        except Exception as e:
            print(f"Could not process {file_path}: {e}")

if __name__ == "__main__":
    fixer = CodeFixer()
    fixer.fix()