import logging
from typing import List, Dict, Any

from app.models import CodeEdit, IssueAnalysis, RootCauseAnalysis
from app.llm.provider import get_llm_provider
from app.llm.prompts import CODE_EDIT_PROMPT

logger = logging.getLogger(__name__)

class PatchGenerator:
    def __init__(self):
        self.llm = get_llm_provider()
        
    def generate_edits(self, file_path: str, file_content: str, symbol_info: Dict[str, Any], 
                      issue_analysis: IssueAnalysis, root_cause: RootCauseAnalysis, plan: str) -> List[CodeEdit]:
        """
        Uses LLM to generate code edits based on the issue analysis, root cause, and plan.
        """
        prompt = CODE_EDIT_PROMPT.format(
            plan=plan,
            file_path=file_path,
            file_content=file_content
        )
        
        system_prompt = "You are a precise patching system. Ensure all old_content exactly matches the provided file_content."
        
        try:
            response_json = self.llm.generate_json(prompt, system_prompt=system_prompt)
            edits_data = response_json.get("edits", [])
            
            valid_edits = []
            for edit_data in edits_data:
                old_content = edit_data.get("old_content", "")
                new_content = edit_data.get("new_content", "")
                reason = edit_data.get("reason", "")
                
                # Validate edit against original file content
                if old_content and old_content not in file_content:
                    logger.warning(f"Generated old_content not found in {file_path}. Edit skipped.")
                    # In a robust system, we might try to fuzzy match or prompt LLM again
                    continue
                    
                valid_edits.append(CodeEdit(
                    file=file_path,
                    old_content=old_content,
                    new_content=new_content,
                    reason=reason
                ))
                
            return valid_edits
            
        except Exception as e:
            logger.error(f"Failed to generate edits for {file_path}: {e}")
            return []
