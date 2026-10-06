import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TestFrameworkDiscovery:
    """Discovers test frameworks and test files within a repository."""
    
    FRAMEWORK_PATTERNS = {
        "python": {
            "pytest": ["pytest"],
            "unittest": ["unittest"],
            "nose": ["nose", "nose2"]
        },
        "javascript": {
            "jest": ["jest"],
            "vitest": ["vitest"],
            "mocha": ["mocha"]
        },
        "java": {
            "junit": ["junit"],
            "testng": ["testng"]
        }
    }

    FILE_PATTERNS = {
        "python": ["test_*.py", "*_test.py"],
        "javascript": ["*.test.js", "*.spec.js", "*.test.ts", "*.spec.ts"],
        "java": ["*Test.java", "*Tests.java", "*TestCase.java"]
    }

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def discover(self) -> Dict[str, str]:
        """Discovers the primary test framework and its command."""
        framework = self.detect_framework()
        if not framework:
            return {}
        
        command = self.detect_command(framework)
        return {
            "framework": framework,
            "command": command
        }

    def detect_framework(self) -> Optional[str]:
        """Detects the test framework from manifest files."""
        manifests = {
            "package.json": self._parse_package_json,
            "pyproject.toml": self._parse_pyproject,
            "requirements.txt": self._parse_requirements,
            "pom.xml": self._parse_pom,
            "build.gradle": self._parse_gradle,
            "Makefile": self._parse_makefile,
            "tox.ini": self._parse_tox
        }

        for manifest, parser in manifests.items():
            manifest_path = self.repo_path / manifest
            if manifest_path.exists():
                try:
                    framework = parser(manifest_path)
                    if framework:
                        return framework
                except Exception as e:
                    logger.error(f"Error parsing {manifest}: {e}")
        return None

    def detect_command(self, framework: str) -> str:
        """Determines the test command for a given framework."""
        commands = {
            "pytest": "pytest",
            "unittest": "python -m unittest",
            "nose": "nosetests",
            "jest": "npm test",
            "vitest": "npm test",
            "mocha": "npm test",
            "junit": "mvn test",
            "testng": "mvn test"
        }
        return commands.get(framework, "test")

    def find_test_files(self, language: str) -> List[str]:
        """Finds test files based on language conventions."""
        patterns = self.FILE_PATTERNS.get(language, [])
        test_files = []
        for pattern in patterns:
            for path in self.repo_path.rglob(pattern):
                if not any(part.startswith('.') or part == 'node_modules' for part in path.parts):
                    test_files.append(str(path.relative_to(self.repo_path)))
        return test_files

    def map_tests_to_source(self, test_files: List[str]) -> Dict[str, str]:
        """Maps test files to their likely source files."""
        mapping = {}
        for test_file in test_files:
            name = Path(test_file).stem
            # Strip common test prefixes/suffixes
            source_name = re.sub(r'^(test_|_test|test|\.test|\.spec)', '', name)
            source_name = re.sub(r'(_test|test|\.test|\.spec)$', '', source_name)
            
            # Simplified matching (in reality, would search repo for source_name.*)
            mapping[test_file] = f"{source_name}{Path(test_file).suffix}"
        return mapping

    def _parse_package_json(self, path: Path) -> Optional[str]:
        content = path.read_text(encoding='utf-8')
        for fw in self.FRAMEWORK_PATTERNS["javascript"]:
            if fw in content:
                return fw
        return None

    def _parse_pyproject(self, path: Path) -> Optional[str]:
        content = path.read_text(encoding='utf-8')
        for fw in self.FRAMEWORK_PATTERNS["python"]:
            if fw in content:
                return fw
        return None

    def _parse_requirements(self, path: Path) -> Optional[str]:
        content = path.read_text(encoding='utf-8')
        for fw in self.FRAMEWORK_PATTERNS["python"]:
            if fw in content:
                return fw
        return None

    def _parse_pom(self, path: Path) -> Optional[str]:
        content = path.read_text(encoding='utf-8')
        for fw in self.FRAMEWORK_PATTERNS["java"]:
            if fw in content:
                return fw
        return None
        
    def _parse_gradle(self, path: Path) -> Optional[str]:
        content = path.read_text(encoding='utf-8')
        for fw in self.FRAMEWORK_PATTERNS["java"]:
            if fw in content:
                return fw
        return None

    def _parse_makefile(self, path: Path) -> Optional[str]:
        content = path.read_text(encoding='utf-8')
        if "pytest" in content: return "pytest"
        if "jest" in content: return "jest"
        return None

    def _parse_tox(self, path: Path) -> Optional[str]:
        content = path.read_text(encoding='utf-8')
        if "pytest" in content: return "pytest"
        return None
