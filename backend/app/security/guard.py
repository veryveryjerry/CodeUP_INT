import re
from typing import Dict
from pathlib import Path

class SecurityGuard:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).resolve()
        
    def redact_secrets(self, text: str) -> str:
        """Redacts potential secrets from strings."""
        if not text:
            return text
            
        # Basic patterns for AWS keys, Generic tokens, etc.
        patterns = [
            (r'(?i)(api_key|apikey|token|password|secret)[\s:=]+["\']?[a-zA-Z0-9_\-]+["\']?', r'\1 = "REDACTED"'),
            (r'AKIA[0-9A-Z]{16}', 'AKIA[REDACTED]'),
            (r'ghp_[a-zA-Z0-9]{36}', 'ghp_[REDACTED]'),
            (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]+', 'Bearer [REDACTED]')
        ]
        
        redacted = text
        for pattern, replacement in patterns:
            redacted = re.sub(pattern, replacement, redacted)
            
        return redacted

    def validate_repo_url(self, url: str) -> bool:
        """Validates repository URLs to only allow specific domains."""
        allowed_domains = ["github.com", "gitlab.com"]
        
        try:
            # Simple parsing without urlparse for speed/simplicity here
            domain_part = url.split("://")[-1].split("/")[0]
            
            # handle git@github.com:...
            if "@" in domain_part:
                domain_part = domain_part.split("@")[-1].split(":")[0]
                
            return any(domain_part == d or domain_part.endswith("." + d) for d in allowed_domains)
        except Exception:
            return False

    def check_suspicious_patterns(self, code: str) -> bool:
        """Checks for suspicious patterns in code before execution."""
        suspicious_patterns = [
            "os.system",
            "subprocess.Popen",
            "eval(",
            "exec(",
            "__import__",
            "require('child_process')"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in code:
                return True
        return False

    def filter_environment(self, env: Dict[str, str]) -> Dict[str, str]:
        """Filters environment variables for subprocess."""
        filtered = {}
        secret_keywords = ["SECRET", "KEY", "TOKEN", "PASSWORD", "CREDENTIAL", "AWS", "GCP", "AZURE"]
        
        for k, v in env.items():
            if any(kw in k.upper() for kw in secret_keywords):
                continue # completely drop them
            filtered[k] = v
        return filtered

    def verify_file_access(self, file_path: str) -> bool:
        """Verifies if file access is only within workspace directory."""
        try:
            target_path = Path(file_path).resolve()
            target_path.relative_to(self.workspace_path)
            return True
        except ValueError:
            return False
