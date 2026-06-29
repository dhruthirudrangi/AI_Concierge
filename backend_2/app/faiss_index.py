import os
import faiss
import numpy as np
from typing import List, Tuple, Dict, Optional
from app.config import EMBEDDING_DIM, IVF_CENTROIDS, IVF_PROBES

class FAIRewardIndex:
    def __init__(self, dimension: int = EMBEDDING_DIM):
        self.dimension = dimension
        self.index: Optional[faiss.Index] = None
        self.card_id_map: List[str] = []  # Maps FAISS index position -> card_id
        self.index_type: str = "Flat"

    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors to unit L2 length so L2 distance represents Cosine Similarity."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1e-9
        return vectors / norms

    def build_flat_index(self, card_ids: List[str], embeddings: np.ndarray):
        """Build a simple exact IndexFlatL2."""
        num_items = len(card_ids)
        if num_items == 0:
            raise ValueError("Cannot build index with zero cards.")
        
        # Ensure correct type and shape
        embeddings = np.ascontiguousarray(embeddings.astype("float32"))
        normalized = self._normalize_vectors(embeddings)
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(normalized)
        
        self.card_id_map = list(card_ids)
        self.index_type = "Flat"
        print(f"Successfully built IndexFlatL2 with {num_items} cards.")

    def build_ivf_index(self, card_ids: List[str], embeddings: np.ndarray, nlist: int = IVF_CENTROIDS):
        """Build an approximate IndexIVFFlat for scaling."""
        num_items = len(card_ids)
        if num_items == 0:
            raise ValueError("Cannot build index with zero cards.")

        # FAISS IVF requires training. Usually requires at least 39 * nlist training vectors.
        min_vectors_required = 39 * nlist
        if num_items < min_vectors_required:
            print(f"Warning: Too few cards ({num_items}) for IVF index training with nlist={nlist} (requires at least {min_vectors_required}). Falling back to IndexFlatL2.")
            self.build_flat_index(card_ids, embeddings)
            return

        embeddings = np.ascontiguousarray(embeddings.astype("float32"))
        normalized = self._normalize_vectors(embeddings)
        
        quantizer = faiss.IndexFlatL2(self.dimension)
        ivf_index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist, faiss.METRIC_L2)
        
        # Train index on normalized vectors
        print(f"Training IndexIVFFlat with {num_items} vectors and {nlist} centroids...")
        ivf_index.train(normalized)
        ivf_index.add(normalized)
        
        # Configure search probes
        ivf_index.nprobe = IVF_PROBES
        
        self.index = ivf_index
        self.card_id_map = list(card_ids)
        self.index_type = "IVF"
        print(f"Successfully built and trained IndexIVFFlat with {num_items} cards.")

    def search(self, query_vector: np.ndarray, k: int = 50) -> List[Tuple[str, float]]:
        """
        Search for nearest neighbor vectors.
        Returns a list of tuples: (card_id, distance)
        Since vectors are L2-normalized:
          d_l2^2 = 2 - 2 * cos_sim
          cos_sim = 1 - (d_l2^2 / 2)
        """
        if self.index is None:
            raise ValueError("Index has not been built or loaded yet.")
        
        # Format query vector
        query_vector = np.ascontiguousarray(query_vector.reshape(1, -1).astype("float32"))
        normalized_query = self._normalize_vectors(query_vector)
        
        # FAISS search
        k = min(k, len(self.card_id_map))
        if k <= 0:
            return []
            
        distances, indices = self.index.search(normalized_query, k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:  # FAISS padding index
                continue
            card_id = self.card_id_map[idx]
            # Convert L2 distance to cosine similarity
            # Clamp value between -1.0 and 1.0
            cos_sim = float(1.0 - (dist / 2.0))
            cos_sim = max(-1.0, min(1.0, cos_sim))
            results.append((card_id, cos_sim))
            
        return results

    def add_card(self, card_id: str, embedding: np.ndarray):
        """Dynamically add a single card vector to the index without rebuild."""
        if self.index is None:
            # Initialize with Flat index if not exists
            self.index = faiss.IndexFlatL2(self.dimension)
            self.card_id_map = []
            self.index_type = "Flat"
            
        embedding = np.ascontiguousarray(embedding.reshape(1, -1).astype("float32"))
        normalized = self._normalize_vectors(embedding)
        
        if self.index_type == "IVF" and not self.index.is_trained:
            raise ValueError("Cannot dynamically add to untrained IVF index.")
            
        self.index.add(normalized)
        self.card_id_map.append(card_id)
        print(f"Dynamically added {card_id} to {self.index_type} FAISS index.")

    def save(self, file_path: str):
        """Save FAISS index and ID mapping."""
        if self.index is None:
            raise ValueError("No index to save.")
            
        # Write index to disk
        faiss.write_index(self.index, file_path)
        
        # Write metadata mapping (id map)
        meta_path = file_path + ".meta"
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.card_id_map))
        print(f"Saved FAISS index and metadata mapping to {file_path}")

    def load(self, file_path: str):
        """Load FAISS index and ID mapping."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"FAISS index file not found at: {file_path}")
            
        self.index = faiss.read_index(file_path)
        
        meta_path = file_path + ".meta"
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"FAISS metadata mapping file not found at: {meta_path}")
            
        with open(meta_path, "r", encoding="utf-8") as f:
            self.card_id_map = [line.strip() for line in f if line.strip()]
            
        # Determine index type
        if isinstance(self.index, faiss.IndexIVFFlat):
            self.index_type = "IVF"
            self.index.nprobe = IVF_PROBES
        else:
            self.index_type = "Flat"
            
        print(f"Loaded {self.index_type} FAISS index with {len(self.card_id_map)} cards.")
