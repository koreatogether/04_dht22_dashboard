# -*- coding: utf-8 -*-
"""
DHT22 프로젝트 Phase 5 테스트
- 배포 및 문서화 테스트
"""
import os
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class TestPhase5:
    """Phase 5 테스트 클래스"""
    def test_dockerfile_exists(None):
        """Dockerfile이 존재하는지 테스트"""
        dockerfile = project_root / "Dockerfile"
        assert dockerfile.exists()
        assert dockerfile.is_file()

    def test_readme_exists(None):
        """README.md 파일이 존재하는지 테스트"""
        readme_file = project_root / "README.MD"
        assert readme_file.exists()
        assert readme_file.is_file()
        # Check if it has substantial content
        assert os.path.getsize(readme_file) > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
