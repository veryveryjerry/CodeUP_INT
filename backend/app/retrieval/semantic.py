import logging
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False

logger = logging.getLogger(__name__)

class SemanticRetrieval:
    def __init__(self, index_path: str = "semantic_index.faiss", meta_path: str = "semantic_meta.json"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.metadata = []
        
        if HAS_SEMANTIC:
            self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')
            self.dimension = self.model.get_sentence_embedding_dimension()
            
            if os.path.exists(index_path) and os.path.exists(meta_path):
                self.index = faiss.read_index(index_path)
                with open(meta_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
        else:
            logger.warning("sentence-transformers or faiss not installed.")
            self.model = None
            self.index = None

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        if not HAS_SEMANTIC:
            return
            
        texts = [chunk.get("content", "") for chunk in chunks]
        if not texts:
            return
            
        embeddings = self.model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
        self.metadata.extend(chunks)
        
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f)

    def search_code(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not HAS_SEMANTIC or not self.metadata:
            return []
            
        query_emb = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_emb).astype('float32'), top_k)
        
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.metadata):
                results.append(self.metadata[idx])
                
        return results
