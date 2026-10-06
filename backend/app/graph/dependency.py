import networkx as nx
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DependencyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, node_type: str, metadata: Dict[str, Any] = None):
        self.graph.add_node(node_id, type=node_type, **(metadata or {}))

    def add_edge(self, source: str, target: str, edge_type: str):
        self.graph.add_edge(source, target, type=edge_type)

    def get_dependencies(self, node: str) -> List[str]:
        if node in self.graph:
            return list(self.graph.successors(node))
        return []

    def get_dependents(self, node: str) -> List[str]:
        if node in self.graph:
            return list(self.graph.predecessors(node))
        return []

    def get_impact_radius(self, node: str) -> List[str]:
        if node in self.graph:
            return list(nx.descendants(self.graph, node))
        return []

    def shortest_path(self, source: str, target: str) -> List[str]:
        try:
            return nx.shortest_path(self.graph, source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def to_json(self) -> str:
        data = nx.node_link_data(self.graph)
        return json.dumps(data)

    def from_json(self, data_str: str):
        data = json.loads(data_str)
        self.graph = nx.node_link_graph(data)
