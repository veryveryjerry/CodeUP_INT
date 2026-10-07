import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    total: int
    passed: int
    failed: int
    errors: int
    test_details: List[Dict]
    stdout: str
    stderr: str
    exit_code: int

class TestExecutor:
    def __init__(self, repo_path: str, timeout: int = 300):
        self.repo_path = repo_path
        self.timeout = timeout

    def run_tests(self, command: str, test_file: Optional[str] = None) -> TestResult:
        full_command = command.split()
        if test_file:
            full_command.append(test_file)
            
        try:
            start_time = time.time()
            process = subprocess.run(
                full_command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout
            )
            
            return self._parse_results(
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.returncode,
                command=command
            )
        except subprocess.TimeoutExpired as e:
            logger.error(f"Test execution timed out after {self.timeout}s")
            return TestResult(
                total=0, passed=0, failed=1, errors=0,
                test_details=[{"name": "timeout", "status": "failed", "error": "timeout"}],
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else "",
                exit_code=-1
            )
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return TestResult(
                total=0, passed=0, failed=1, errors=1,
                test_details=[{"name": "execution_error", "status": "error", "error": str(e)}],
                stdout="", stderr=str(e), exit_code=-2
            )

    def _parse_results(self, stdout: str, stderr: str, exit_code: int, command: str) -> TestResult:
        # Simplistic parsing logic. Real implementation would use formatters like pytest-json-report
        passed, failed, errors, total = 0, 0, 0, 0
        details = []

        if "pytest" in command:
            if "passed" in stdout: passed = stdout.count("PASSED")
            if "failed" in stdout: failed = stdout.count("FAILED")
            if "error" in stdout: errors = stdout.count("ERROR")
            total = passed + failed + errors
        elif "npm test" in command or "jest" in command:
            if "Tests:" in stdout:
                # Naive parsing
                pass
                
        return TestResult(
            total=total,
            passed=passed,
            failed=failed,
            errors=errors,
            test_details=details,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code
        )
