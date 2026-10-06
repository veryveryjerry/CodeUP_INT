import logging
import hashlib
import os
from typing import Dict, List, Any, Optional

try:
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript  
    import tree_sitter_typescript as tstypescript
    import tree_sitter_java as tsjava
    from tree_sitter import Language, Parser
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

logger = logging.getLogger(__name__)

class SymbolExtractor:
    def __init__(self):
        self.parsers = {}
        self.file_hashes = {}
        if HAS_TREE_SITTER:
            self.langs = {
                ".py": Language(tspython.language()),
                ".js": Language(tsjavascript.language()),
                ".ts": Language(tstypescript.language_typescript()),
                ".java": Language(tsjava.language())
            }
            for ext, lang in self.langs.items():
                parser = Parser(lang)
                self.parsers[ext] = parser

    def get_file_hash(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        if not HAS_TREE_SITTER:
            logger.error("tree_sitter is not installed.")
            return []

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.parsers:
            return []
            
        current_hash = self.get_file_hash(file_path)
        if self.file_hashes.get(file_path) == current_hash:
            logger.info(f"Skipping unchanged file {file_path}")
            return []

        self.file_hashes[file_path] = current_hash
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []

        parser = self.parsers[ext]
        tree = parser.parse(bytes(source_code, "utf8"))
        lang = self.langs[ext]
        
        symbols = []
        if ext == ".py":
            symbols = self._extract_python_symbols(tree, lang, source_code, file_path)
            
        return symbols

    def _extract_python_symbols(self, tree, lang, source_code: str, file_path: str) -> List[Dict[str, Any]]:
        symbols = []
        query_str = """
        (function_definition
            name: (identifier) @func.name
            parameters: (parameters) @func.params
            return_type: (type)? @func.return
        ) @function
        (class_definition
            name: (identifier) @class.name
        ) @class
        (import_statement) @import
        (import_from_statement) @import_from
        """
        try:
            query = lang.query(query_str)
            captures = query.captures(tree.root_node)
            
            for node, name in captures.items():
                if name == "func.name":
                    symbols.append({
                        "type": "function",
                        "name": source_code[node.start_byte:node.end_byte],
                        "file": file_path,
                        "line_start": node.start_point[0],
                        "line_end": node.end_point[0]
                    })
                elif name == "class.name":
                    symbols.append({
                        "type": "class",
                        "name": source_code[node.start_byte:node.end_byte],
                        "file": file_path,
                        "line_start": node.start_point[0],
                        "line_end": node.end_point[0]
                    })
        except Exception as e:
            logger.error(f"Query error in python parser: {e}")
            
        return symbols
