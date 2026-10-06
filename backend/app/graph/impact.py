import logging
from typing import List, Dict, Any, Set
from pydantic import BaseModel
from .dependency import DependencyGraph

logger = logging.getLogger(__name__)

class ImpactRadius(BaseModel):
    directly_affected: List[str]
    indirectly_affected: List[str]
    affected_tests: List[str]
    risk_score: float

class ImpactAnalyzer:
    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def calculate_impact(self, changed_symbols: List[str]) -> ImpactRadius:
        direct = set()
        indirect = set()
        tests = set()
        
        for symbol in changed_symbols:
            deps = self.graph.get_dependents(symbol)
            direct.update(deps)
            
            all_deps = self.graph.get_impact_radius(symbol)
            indirect.update(all_deps)
            
        indirect = indirect - direct
        
        for node in (direct | indirect):
            node_data = self.graph.graph.nodes.get(node, {})
            if node_data.get("type") == "test" or "test" in node.lower():
                tests.add(node)
                
        risk_score = min(1.0, (len(direct) * 2 + len(indirect) + len(tests) * 0.5) / 100.0)
        
        return ImpactRadius(
            directly_affected=list(direct),
            indirectly_affected=list(indirect),
            affected_tests=list(tests),
            risk_score=risk_score
        )
