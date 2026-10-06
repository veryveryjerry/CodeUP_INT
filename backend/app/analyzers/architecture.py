import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ArchitectureAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def detect_layers(self) -> Dict[str, List[str]]:
        layers = {
            "frontend": [],
            "api": [],
            "service": [],
            "repository": [],
            "database": []
        }
        for root, dirs, files in os.walk(self.repo_path):
            if any(ignore in root for ignore in [".git", "node_modules", "venv"]):
                continue
            
            for file in files:
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, self.repo_path).lower()
                
                if "components" in rel_path or "views" in rel_path or "pages" in rel_path:
                    layers["frontend"].append(rel_path)
                elif "api" in rel_path or "controllers" in rel_path or "routes" in rel_path:
                    layers["api"].append(rel_path)
                elif "services" in rel_path:
                    layers["service"].append(rel_path)
                elif "repositories" in rel_path or "dao" in rel_path:
                    layers["repository"].append(rel_path)
                elif "models" in rel_path or "entities" in rel_path or "db" in rel_path:
                    layers["database"].append(rel_path)
                    
        return layers

    def detect_entry_points(self) -> List[str]:
        entry_points = []
        candidates = ["main.py", "app.py", "index.js", "server.js", "manage.py", "wsgi.py"]
        for root, _, files in os.walk(self.repo_path):
            if any(ignore in root for ignore in [".git", "node_modules", "venv"]):
                continue
            for file in files:
                if file in candidates:
                    entry_points.append(os.path.relpath(os.path.join(root, file), self.repo_path))
        return entry_points

    def detect_config_files(self) -> List[str]:
        configs = []
        candidates = [".env", "config.py", "settings.py", "application.yml", "application.properties", "docker-compose.yml", "Dockerfile"]
        for root, _, files in os.walk(self.repo_path):
            if any(ignore in root for ignore in [".git", "node_modules", "venv"]):
                continue
            for file in files:
                if file in candidates or file.endswith(".json") or file.endswith(".yaml") or file.endswith(".yml"):
                    configs.append(os.path.relpath(os.path.join(root, file), self.repo_path))
        return configs

    def generate_summary(self) -> Dict[str, Any]:
        return {
            "layers": self.detect_layers(),
            "entry_points": self.detect_entry_points(),
            "config_files": self.detect_config_files()
        }
