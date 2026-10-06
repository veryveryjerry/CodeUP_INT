import logging
from typing import List

from app.models import CodeEdit

logger = logging.getLogger(__name__)

class PatchOptimizer:
    def __init__(self):
        pass
        
    def calculate_cost(self, edits: List[CodeEdit]) -> float:
        """
        Calculate PatchCost: files_changed + lines_added + lines_deleted + 
        public_interfaces_changed + dependency_changes + risk_score
        """
        files_changed = len(set(edit.file for edit in edits))
        lines_added = sum(edit.new_content.count('\n') for edit in edits)
        lines_deleted = sum(edit.old_content.count('\n') for edit in edits)
        
        # Simplified risk score and other metrics for this implementation
        public_interfaces_changed = 0
        dependency_changes = 0
        risk_score = 0.5 * files_changed
        
        cost = files_changed + lines_added + lines_deleted + public_interfaces_changed + dependency_changes + risk_score
        return cost

    def select_best_patch(self, proposals: List[List[CodeEdit]]) -> List[CodeEdit]:
        """If multiple patches proposed, select lowest cost"""
        if not proposals:
            return []
            
        scored_proposals = [(self.calculate_cost(patch), patch) for patch in proposals]
        scored_proposals.sort(key=lambda x: x[0])
        
        return scored_proposals[0][1]
        
    def validate_patch(self, edits: List[CodeEdit], max_files: int = 5) -> bool:
        """
        Reject patches that touch too many unrelated files
        Validate no unnecessary formatting changes
        """
        files_changed = len(set(edit.file for edit in edits))
        if files_changed > max_files:
            logger.warning(f"Patch rejected: touches too many files ({files_changed} > {max_files})")
            return False
            
        # Basic check for unnecessary formatting (if only whitespace changed)
        for edit in edits:
            if edit.old_content.strip() == edit.new_content.strip() and edit.old_content != edit.new_content:
                logger.warning("Patch rejected: contains unnecessary formatting changes")
                return False
                
        return True
