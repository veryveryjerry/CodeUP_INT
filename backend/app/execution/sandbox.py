import subprocess
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Dict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int
    duration: float

class CommandExecutor:
    ALLOWED_COMMANDS = {
        "git", "python", "pytest", "npm", "node", "mvn", "gradle", "ruff", "eslint", "tsc", "pip"
    }
    
    BLOCKED_PATTERNS = [
        "rm -rf /", "mkfs", "format", "dd", "> /dev/sda"
    ]

    def __init__(self, workspace_path: str, timeout: int = 120):
        self.workspace_path = Path(workspace_path).resolve()
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None

    def execute(self, command: str, cwd: Optional[str] = None) -> CommandResult:
        if not self._is_command_allowed(command):
            return CommandResult("", f"Command not allowed or blocked: {command}", -1, 0.0)

        work_dir = self.workspace_path
        if cwd:
            requested_dir = (self.workspace_path / cwd).resolve()
            if not self._is_within_workspace(requested_dir):
                return CommandResult("", "Working directory outside workspace is not allowed.", -1, 0.0)
            work_dir = requested_dir

        env = self._filter_env(os.environ.copy())
        
        start_time = time.time()
        try:
            self.process = subprocess.Popen(
                command,
                shell=True,
                cwd=str(work_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = self.process.communicate(timeout=self.timeout)
            exit_code = self.process.returncode
        except subprocess.TimeoutExpired:
            self.cancel()
            duration = time.time() - start_time
            return CommandResult("", "Command execution timed out.", -1, duration)
        except Exception as e:
            duration = time.time() - start_time
            return CommandResult("", str(e), -1, duration)
        finally:
            self.process = None

        duration = time.time() - start_time
        return CommandResult(stdout, stderr, exit_code, duration)

    def cancel(self):
        """Cancels the currently running process."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def _is_command_allowed(self, command: str) -> bool:
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
            
        base_cmd = cmd_parts[0]
        if base_cmd not in self.ALLOWED_COMMANDS:
            return False
            
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in command:
                return False
                
        return True

    def _is_within_workspace(self, path: Path) -> bool:
        try:
            path.relative_to(self.workspace_path)
            return True
        except ValueError:
            return False

    def _filter_env(self, env: Dict[str, str]) -> Dict[str, str]:
        """Redacts secrets from environment variables."""
        filtered = {}
        secret_keywords = ["SECRET", "KEY", "TOKEN", "PASSWORD", "CREDENTIAL"]
        
        for k, v in env.items():
            if any(kw in k.upper() for kw in secret_keywords):
                filtered[k] = "REDACTED"
            else:
                filtered[k] = v
        return filtered
