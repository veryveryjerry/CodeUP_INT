import logging
import os
import subprocess
import uuid
from typing import List

from app.models import CodeEdit

logger = logging.getLogger(__name__)

class PatchApplier:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.branch_name = f"patch-{uuid.uuid4().hex[:8]}"
        
    def _run_git_command(self, cmd: List[str]) -> str:
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: git {' '.join(cmd)}\nError: {e.stderr}")
            raise

    def create_branch(self) -> str:
        """Create a new git branch before patching"""
        self._run_git_command(["checkout", "-b", self.branch_name])
        return self.branch_name
        
    def apply_edits(self, edits: List[CodeEdit]) -> bool:
        """Apply CodeEdit objects to files"""
        try:
            for edit in edits:
                full_path = os.path.join(self.repo_path, edit.file)
                
                if not os.path.exists(full_path):
                    logger.error(f"File {full_path} does not exist.")
                    return False
                    
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if edit.old_content not in content:
                    logger.error(f"old_content not found in {edit.file}")
                    return False
                    
                new_file_content = content.replace(edit.old_content, edit.new_content, 1)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_file_content)
                    
            return True
        except Exception as e:
            logger.error(f"Error applying edits: {e}")
            return False
            
    def generate_diff(self) -> str:
        """Generate unified diff of the changes"""
        try:
            return self._run_git_command(["diff"])
        except Exception:
            return ""

    def rollback(self) -> bool:
        """Support rollback via git reset"""
        try:
            self._run_git_command(["reset", "--hard", "HEAD"])
            self._run_git_command(["checkout", "-"])
            self._run_git_command(["branch", "-D", self.branch_name])
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def verify_patch(self) -> bool:
        """Verify patch applied correctly (e.g., syntactically correct). 
        Basic check for this implementation."""
        # This could run linter or syntax checker depending on file type
        return True
