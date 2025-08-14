"""
Automatically fixes MyPy type hint errors.
"""
import re
from pathlib import Path


class TypeHintFixer:
    def __init__(self, project_root=".") -> None:
        self.project_root = Path(project_root)

    def fix(self) -> None:
        print("Fixing missing type hints...")
        for file_path in self.project_root.rglob("*.py"):
            self.fix_file(file_path)

    def fix_file(self, file_path: Path) -> None:
        try:
            with file_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            modified = False
            for line in lines:
                # Add '-> None' to functions without return type hints
                if re.match(r"^\s*def\s+\w+\(.*\):\s*$", line):
                    new_line = line.strip() + " -> None:\n"
                    if new_line != line:
                        new_lines.append(new_line)
                        modified = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            if modified:
                print(f"  - Adding type hints to {file_path}")
                with file_path.open("w", encoding="utf-8") as f:
                    f.writelines(new_lines)
        except Exception as e:
            print(f"Could not process {file_path}: {e}")


if __name__ == "__main__":
    fixer = TypeHintFixer()
    fixer.fix()
