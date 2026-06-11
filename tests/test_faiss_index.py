import os
import tempfile
import numpy as np
import pytest
from app.faiss_index import FAIRewardIndex

def test_flat_index_build_and_search():
    index = FAIRewardIndex(dimension=8)
    card_ids = ["card_a", "card_b", "card_c"]
    
    # 3 mock embeddings (8-dim)
    embeddings = np.array([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # card_a
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # card_b
        [0.7, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]   # card_c
    ], dtype="float32")
    
    index.build_flat_index(card_ids, embeddings)
    assert index.index_type == "Flat"
    assert len(index.card_id_map) == 3
    
    # Query close to card_a
    query = np.array([0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype="float32")
    results = index.search(query, k=2)
    
    assert len(results) == 2
    assert results[0][0] == "card_a"
    assert results[0][1] > results[1][1]  # card_a is closer than card_c

def test_ivf_index_fallback_and_training():
    dimension = 4
    index = FAIRewardIndex(dimension=dimension)
    
    # If we have very few cards, building IVF should fall back to Flat
    card_ids = [f"c_{i}" for i in range(10)]
    embeddings = np.random.randn(10, dimension).astype("float32")
    
    index.build_ivf_index(card_ids, embeddings, nlist=5)
    assert index.index_type == "Flat"  # Fallback to Flat because 10 < 39 * 5 (195)
    
    # Let's train a valid IVF index by generating enough vectors.
    # Set nlist to 2, which requires at least 78 vectors.
    nlist = 2
    count = 80
    card_ids_large = [f"c_{i}" for i in range(count)]
    embeddings_large = np.random.randn(count, dimension).astype("float32")
    
    index_large = FAIRewardIndex(dimension=dimension)
    index_large.build_ivf_index(card_ids_large, embeddings_large, nlist=nlist)
    assert index_large.index_type == "IVF"
    assert len(index_large.card_id_map) == count
    
    # Search IVF
    query = np.random.randn(dimension).astype("float32")
    results = index_large.search(query, k=5)
    assert len(results) == 5

def test_dynamic_add():
    index = FAIRewardIndex(dimension=4)
    # Start blank
    index.add_card("card_new", np.array([1.0, 0.0, 0.0, 0.0], dtype="float32"))
    
    assert index.index_type == "Flat"
    assert index.card_id_map == ["card_new"]
    
    results = index.search(np.array([1.0, 0.0, 0.0, 0.0], dtype="float32"), k=1)
    assert results[0][0] == "card_new"
    assert abs(results[0][1] - 1.0) < 1e-5  # Cosine similarity 1.0

def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "test_index.bin")
        
        index = FAIRewardIndex(dimension=4)
        card_ids = ["c1", "c2"]
        embeddings = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype="float32")
        
        index.build_flat_index(card_ids, embeddings)
        index.save(index_path)
        
        # Reload
        loaded_index = FAIRewardIndex(dimension=4)
        loaded_index.load(index_path)
        
        assert loaded_index.index_type == "Flat"
        assert loaded_index.card_id_map == ["c1", "c2"]
        
        results = loaded_index.search(np.array([1.0, 0.0, 0.0, 0.0], dtype="float32"), k=1)
        assert results[0][0] == "c1"
