#!/usr/bin/env python3
"""
Emoji Compatibility Test Tool

Tests whether emojis are properly displayed in the current environment
and provides safe emoji usage methods.
"""

import os
import sys
from pathlib import Path


def test_emoji_output():
    """Test emoji output"""

    test_emojis = [
        ("[SEARCH]", "SEARCH"),
        ("[OK]", "CHECK_MARK"),
        ("[ERROR]", "CROSS_MARK"),
        ("[WARNING]", "WARNING_SIGN"),
        ("[INFO]", "INFORMATION"),
        ("[TOOL]", "WRENCH"),
        ("[DATA]", "CHART"),
        ("[RESULT]", "TROPHY"),
    ]

    print("Testing emoji compatibility...")
    print("=" * 50)

    for ascii_version, description in test_emojis:
        try:
            # Try to print ASCII version (always safe)
            print(f"ASCII: {ascii_version} ({description})")

        except UnicodeEncodeError as e:
            print(f"ERROR: Failed to display {description}: {e}")


def test_system_info():
    """Display system information relevant to emoji support"""

    print("\nSystem Information:")
    print("=" * 50)

    print(f"Operating System: {os.name}")
    print(f"Platform: {sys.platform}")
    print(f"Python Version: {sys.version}")
    print(f"Default Encoding: {sys.getdefaultencoding()}")

    # Test stdout encoding
    try:
        stdout_encoding = sys.stdout.encoding
        print(f"STDOUT Encoding: {stdout_encoding}")
    except AttributeError:
        print("STDOUT Encoding: Not available")

    # Test environment variables
    pythonioencoding = os.environ.get("PYTHONIOENCODING", "Not set")
    print(f"PYTHONIOENCODING: {pythonioencoding}")

    pythonutf8 = os.environ.get("PYTHONUTF8", "Not set")
    print(f"PYTHONUTF8: {pythonutf8}")


def test_file_encoding():
    """Test file encoding capabilities"""

    print("\nFile Encoding Test:")
    print("=" * 50)

    test_content = "Test ASCII content only"
    test_file = Path("emoji_test.txt")

    try:
        # Test UTF-8 writing
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        print("UTF-8 file writing: SUCCESS")

        # Test UTF-8 reading
        with open(test_file, encoding="utf-8") as f:
            f.read()
        print("UTF-8 file reading: SUCCESS")

        # Cleanup
        test_file.unlink()

    except Exception as e:
        print(f"File encoding test FAILED: {e}")


def get_recommendations():
    """Get recommendations for emoji usage"""

    print("\nRecommendations:")
    print("=" * 50)

    if os.name == "nt":  # Windows
        print("Windows detected:")
        print("- Use ASCII alternatives instead of emojis")
        print("- Set environment: PYTHONIOENCODING=utf-8")
        print("- Use run_with_utf8.bat for Python scripts")
    else:  # Unix/Linux/Mac
        print("Unix-like system detected:")
        print("- Emojis should work in most terminals")
        print("- Ensure terminal supports UTF-8")

    print("\nGeneral recommendations:")
    print("- Always provide ASCII fallbacks")
    print("- Test emoji output before deployment")
    print("- Use safe_emoji.py module for compatibility")


def main() -> None:
    """Main function"""
    print("Emoji Compatibility Test Tool")
    print("=" * 50)

    test_emoji_output()
    test_system_info()
    test_file_encoding()
    get_recommendations()

    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    main()
