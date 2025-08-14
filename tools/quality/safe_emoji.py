#!/usr/bin/env python3
"""
Safe Emoji Output Module

Selectively uses emojis or ASCII replacement characters based on environment.
"""

import os
import sys


class SafeEmoji:
    """Safe emoji output class"""

    def __init__(self):
        self.emoji_support = self._test_emoji_support()

        # Emoji to ASCII replacement mapping
        self.emoji_map = {
            "search": ("[SEARCH]", "[SCAN]"),
            "success": ("[SUCCESS]", "[OK]"),
            "error": ("[ERROR]", "[ERR]"),
            "warning": ("[WARNING]", "[WARN]"),
            "info": ("[INFO]", "[NOTE]"),
            "tool": ("[TOOL]", "[APP]"),
            "data": ("[DATA]", "[INFO]"),
            "result": ("[RESULT]", "[END]"),
            "tip": ("[TIP]", "[HINT]"),
        }

    def _test_emoji_support(self) -> bool:
        """Test if current environment supports emoji output"""
        try:
            # Windows Command Prompt usually doesn't support emojis well
            if os.name == "nt":
                return False
            
            # Test basic emoji encoding capability
            test_emoji = "✅"
            test_emoji.encode(sys.stdout.encoding or "utf-8")
            return True
            
        except (UnicodeEncodeError, AttributeError):
            return False
    
    def get(self, emoji_name: str, fallback_index: int = 0) -> str:
        """Get emoji or ASCII replacement based on environment"""
        if emoji_name in self.emoji_map:
            options = self.emoji_map[emoji_name]
            if self.emoji_support and len(options) > 1:
                return options[1]  # Use emoji version
            else:
                return options[0]  # Use ASCII version
        else:
            return f"[{emoji_name.upper()}]"  # Default ASCII format


# Global instance for easy access
safe_emoji = SafeEmoji()


def get_safe_emoji(name: str) -> str:
    """Convenience function to get safe emoji"""
    return safe_emoji.get(name)


def print_with_safe_emoji(emoji_name: str, message: str) -> None:
    """Print message with safe emoji prefix"""
    prefix = safe_emoji.get(emoji_name)
    print(f"{prefix} {message}")


if __name__ == "__main__":
    # Test emoji support
    print("Testing emoji support...")
    print(f"Emoji support detected: {safe_emoji.emoji_support}")
    
    print("\nTesting emoji output:")
    for name in safe_emoji.emoji_map.keys():
        emoji = safe_emoji.get(name)
        print(f"{emoji} Testing {name}")