import subprocess
import os
from typing import List, Dict, Any

class StaticAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def analyze(self, files: List[str]) -> List[Dict[str, Any]]:
        issues = []
        for file in files:
            issues.extend(self._analyze_file(file))
        return issues

    def _analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        issues = []
        full_path = os.path.join(self.repo_path, file_path)
        
        if not os.path.exists(full_path):
            return issues

        # Check for Python
        if file_path.endswith('.py'):
            try:
                # Syntax check
                with open(full_path, "r", encoding="utf-8") as f:
                    compile(f.read(), full_path, 'exec')
                    
                # Run ruff if available
                res = subprocess.run(["ruff", "check", full_path], capture_output=True, text=True)
                if res.returncode != 0:
                    issues.append({"file": file_path, "tool": "ruff", "message": res.stdout})
            except SyntaxError as e:
                issues.append({"file": file_path, "tool": "syntax", "message": str(e)})
            except FileNotFoundError:
                pass # ruff not installed
                
        # Check for JS/TS
        elif file_path.endswith('.js') or file_path.endswith('.ts'):
            try:
                # Run eslint if available
                res = subprocess.run(["npx", "eslint", full_path], cwd=self.repo_path, capture_output=True, text=True)
                if res.returncode != 0:
                    issues.append({"file": file_path, "tool": "eslint", "message": res.stdout})
                    
                if file_path.endswith('.ts'):
                    res = subprocess.run(["npx", "tsc", "--noEmit", full_path], cwd=self.repo_path, capture_output=True, text=True)
                    if res.returncode != 0:
                        issues.append({"file": file_path, "tool": "tsc", "message": res.stdout})
            except FileNotFoundError:
                pass # npx not available

        return issues
