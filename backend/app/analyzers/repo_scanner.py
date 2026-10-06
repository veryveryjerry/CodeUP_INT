import os
import shutil
import sqlite3
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from git import Repo
import json
import hashlib

logger = logging.getLogger(__name__)

class RepositoryInfo:
    def __init__(self, name: str, path: str, primary_language: str, frameworks: List[str], 
                 package_managers: List[str], test_frameworks: List[str], build_systems: List[str]):
        self.name = name
        self.path = path
        self.primary_language = primary_language
        self.frameworks = frameworks
        self.package_managers = package_managers
        self.test_frameworks = test_frameworks
        self.build_systems = build_systems
        
    def to_dict(self):
        return {
            "name": self.name,
            "path": self.path,
            "primary_language": self.primary_language,
            "frameworks": self.frameworks,
            "package_managers": self.package_managers,
            "test_frameworks": self.test_frameworks,
            "build_systems": self.build_systems
        }

class RepositoryScanner:
    IGNORE_DIRS = {".git", "node_modules", "venv", "__pycache__", "dist", "build", ".tox", ".idea", ".vscode"}
    
    def __init__(self, db_path: str = "repo_scanner.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repo_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_path TEXT,
                file_path TEXT,
                extension TEXT,
                size INTEGER,
                hash TEXT,
                last_modified REAL
            )
        ''')
        conn.commit()
        conn.close()

    def clone_repository(self, url: str, dest: str) -> str:
        logger.info(f"Cloning {url} into {dest}")
        if os.path.exists(dest):
            shutil.rmtree(dest)
        Repo.clone_from(url, dest)
        return dest

    def scan_files(self, repo_path: str) -> List[Dict[str, Any]]:
        repo_map = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                try:
                    stats = os.stat(file_path)
                    ext = os.path.splitext(file)[1].lower()
                    
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        
                    file_info = {
                        "repo_path": repo_path,
                        "file_path": rel_path,
                        "extension": ext,
                        "size": stats.st_size,
                        "hash": file_hash,
                        "last_modified": stats.st_mtime
                    }
                    repo_map.append(file_info)
                    
                    cursor.execute('''
                        INSERT INTO repo_files (repo_path, file_path, extension, size, hash, last_modified)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (repo_path, rel_path, ext, stats.st_size, file_hash, stats.st_mtime))
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    
        conn.commit()
        conn.close()
        return repo_map

    def detect_language(self, repo_map: List[Dict[str, Any]]) -> str:
        ext_counts = {}
        for file in repo_map:
            ext = file["extension"]
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
            
        if not ext_counts:
            return "Unknown"
            
        ext_to_lang = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".java": "Java", ".cpp": "C++", ".c": "C", ".go": "Go",
            ".rs": "Rust", ".rb": "Ruby", ".php": "PHP"
        }
        
        sorted_exts = sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)
        for ext, _ in sorted_exts:
            if ext in ext_to_lang:
                return ext_to_lang[ext]
        return "Unknown"

    def detect_frameworks(self, repo_path: str) -> List[str]:
        frameworks = []
        req_txt = os.path.join(repo_path, "requirements.txt")
        pkg_json = os.path.join(repo_path, "package.json")
        pom_xml = os.path.join(repo_path, "pom.xml")
        
        if os.path.exists(req_txt):
            with open(req_txt, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "django" in content: frameworks.append("Django")
                if "flask" in content: frameworks.append("Flask")
                if "fastapi" in content: frameworks.append("FastAPI")
                
        if os.path.exists(pkg_json):
            try:
                with open(pkg_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    if "express" in deps: frameworks.append("Express")
                    if "react" in deps: frameworks.append("React")
            except Exception as e:
                logger.error(f"Error parsing package.json: {e}")
                
        if os.path.exists(pom_xml):
            with open(pom_xml, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "spring" in content: frameworks.append("Spring")
                
        return list(set(frameworks))

    def detect_package_managers(self, repo_path: str) -> List[str]:
        pms = []
        if os.path.exists(os.path.join(repo_path, "requirements.txt")) or os.path.exists(os.path.join(repo_path, "Pipfile")): pms.append("pip")
        if os.path.exists(os.path.join(repo_path, "package.json")):
            if os.path.exists(os.path.join(repo_path, "yarn.lock")): pms.append("yarn")
            else: pms.append("npm")
        if os.path.exists(os.path.join(repo_path, "pom.xml")): pms.append("maven")
        if os.path.exists(os.path.join(repo_path, "build.gradle")): pms.append("gradle")
        return pms

    def detect_test_frameworks(self, repo_path: str) -> List[str]:
        tests = []
        req_txt = os.path.join(repo_path, "requirements.txt")
        pkg_json = os.path.join(repo_path, "package.json")
        pom_xml = os.path.join(repo_path, "pom.xml")
        
        if os.path.exists(req_txt):
            with open(req_txt, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "pytest" in content: tests.append("pytest")
                
        if os.path.exists(pkg_json):
            try:
                with open(pkg_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    if "jest" in deps: tests.append("jest")
                    if "vitest" in deps: tests.append("vitest")
            except Exception as e:
                pass
                
        if os.path.exists(pom_xml):
            with open(pom_xml, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "junit" in content: tests.append("junit")
                
        return list(set(tests))

    def detect_build_systems(self, repo_path: str) -> List[str]:
        builds = []
        if os.path.exists(os.path.join(repo_path, "Makefile")): builds.append("make")
        if os.path.exists(os.path.join(repo_path, "CMakeLists.txt")): builds.append("cmake")
        if os.path.exists(os.path.join(repo_path, "build.gradle")): builds.append("gradle")
        if os.path.exists(os.path.join(repo_path, "pom.xml")): builds.append("maven")
        if os.path.exists(os.path.join(repo_path, "webpack.config.js")): builds.append("webpack")
        return builds

    def scan(self, repo_path: str) -> RepositoryInfo:
        repo_name = os.path.basename(os.path.normpath(repo_path))
        repo_map = self.scan_files(repo_path)
        lang = self.detect_language(repo_map)
        frameworks = self.detect_frameworks(repo_path)
        pms = self.detect_package_managers(repo_path)
        tests = self.detect_test_frameworks(repo_path)
        builds = self.detect_build_systems(repo_path)
        
        return RepositoryInfo(
            name=repo_name,
            path=repo_path,
            primary_language=lang,
            frameworks=frameworks,
            package_managers=pms,
            test_frameworks=tests,
            build_systems=builds
        )
