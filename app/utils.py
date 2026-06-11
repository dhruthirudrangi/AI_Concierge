import numpy as np
from typing import List, Dict, Set

def compute_dcg(relevances: List[float]) -> float:
    """Compute Discounted Cumulative Gain (DCG)."""
    dcg = 0.0
    for idx, rel in enumerate(relevances):
        # 1-indexed formula
        dcg += (2**rel - 1.0) / np.log2(idx + 2)
    return dcg

def compute_ndcg(recommended_ids: List[str], ground_truth_relevance: Dict[str, float], k: int = 5) -> float:
    """
    Compute Normalized Discounted Cumulative Gain (NDCG) at K.
    ground_truth_relevance is a dictionary mapping card_id -> relevance score.
    """
    recommended_ids = recommended_ids[:k]
    relevances = [ground_truth_relevance.get(cid, 0.0) for cid in recommended_ids]
    
    dcg = compute_dcg(relevances)
    
    # Calculate Ideal DCG (IDCG)
    # Sort all ground truth relevances in descending order
    all_relevances = list(ground_truth_relevance.values())
    ideal_relevances = sorted(all_relevances, reverse=True)[:k]
    
    # If no relevant items exist at all, NDCG is 1.0 (or 0.0). We return 1.0 by convention.
    if not ideal_relevances or sum(ideal_relevances) == 0.0:
        return 1.0
        
    idcg = compute_dcg(ideal_relevances)
    return float(dcg / idcg)

def compute_mrr(recommended_ids: List[str], ground_truth_relevant_ids: Set[str]) -> float:
    """
    Compute Mean Reciprocal Rank (MRR).
    Returns 1/r where r is the 1-based rank of the first relevant item.
    Returns 0.0 if no relevant items are found.
    """
    for idx, cid in enumerate(recommended_ids):
        if cid in ground_truth_relevant_ids:
            return 1.0 / (idx + 1)
    return 0.0
