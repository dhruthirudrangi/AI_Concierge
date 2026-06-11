import time
import numpy as np
from typing import List, Dict, Tuple, Set
from app.config import EMBEDDING_DIM
from app.data_store import generate_mock_cards, UserProfile
from app.faiss_index import FAIRewardIndex
from app.business_rules import BusinessRulesEngine
from app.re_ranking import ReRanker
from app.utils import compute_ndcg, compute_mrr

def run_scale_benchmark(scale: int) -> Dict[str, float]:
    print(f"\n--- Running Benchmark for Scale: {scale} cards ---")
    
    # 1. Generate data
    start = time.perf_counter()
    cards = generate_mock_cards(scale)
    card_ids = [c.card_id for c in cards]
    data_gen_time = (time.perf_counter() - start) * 1000
    print(f"Generated data in {data_gen_time:.2f}ms")
    
    # Generate random card embeddings
    np.random.seed(42)
    embeddings = np.random.randn(scale, EMBEDDING_DIM).astype("float32")
    
    # 2. Build indices
    # Exact Flat Index
    start = time.perf_counter()
    flat_index = FAIRewardIndex(dimension=EMBEDDING_DIM)
    flat_index.build_flat_index(card_ids, embeddings)
    flat_build_time = (time.perf_counter() - start) * 1000
    
    # IVF Index
    start = time.perf_counter()
    ivf_index = FAIRewardIndex(dimension=EMBEDDING_DIM)
    # Using 100 centroids for 1K/10K. For 100 cards, use 5 centroids.
    nlist = 100 if scale >= 1000 else 5
    ivf_index.build_ivf_index(card_ids, embeddings, nlist=nlist)
    ivf_build_time = (time.perf_counter() - start) * 1000
    
    # 3. Simulate Queries
    num_queries = 50
    query_vectors = np.random.randn(num_queries, EMBEDDING_DIM).astype("float32")
    
    # Setup test user and components
    user = UserProfile(
        user_id="benchmark_user",
        name="Benchmark User",
        balance=4200,
        region="US",
        spending_habits={"travel": 0.40, "dining": 0.30, "grocery": 0.20, "shopping": 0.10},
        eligibility_tier="Gold",
        preferences=["travel rewards", "dining discounts"]
    )
    rules_engine = BusinessRulesEngine()
    
    # Benchmarking query performance
    flat_latencies = []
    ivf_latencies = []
    rerank_latencies = []
    ndcg_scores = []
    
    for q_idx in range(num_queries):
        qv = query_vectors[q_idx]
        
        # A. Flat Index Search
        t0 = time.perf_counter()
        flat_results = flat_index.search(qv, k=50)
        flat_latencies.append((time.perf_counter() - t0) * 1000)
        
        # B. IVF Index Search
        t0 = time.perf_counter()
        ivf_results = ivf_index.search(qv, k=50)
        ivf_latencies.append((time.perf_counter() - t0) * 1000)
        
        # C. Re-ranking & Filtering overhead
        # Run rules & ranking on the top 50 retrieved IVF candidates
        t0 = time.perf_counter()
        # Retrieve candidate cards from DB mapping
        candidate_ids = [item[0] for item in ivf_results]
        candidate_cards = [cards[int(cid.split("_")[1])] for cid in candidate_ids]
        
        filtered = rules_engine.run_filtering_pipeline(candidate_cards, user)
        
        sim_map = {cid: sim for cid, sim in ivf_results}
        final_picks = ReRanker.re_rank(
            candidates=filtered,
            similarity_map=sim_map,
            user=user,
            category_affinity={},
            disliked_card_ids=set(),
            top_n=5
        )
        rerank_latencies.append((time.perf_counter() - t0) * 1000)
        
        # D. Accuracy evaluation: NDCG of IVF compared to Flat
        # Ground truth relevance: 3.0 for top 5, 2.0 for next 15, 1.0 for rest of the Flat results
        relevance_dict = {}
        for rank, (cid, sim) in enumerate(flat_results):
            if rank < 5:
                relevance_dict[cid] = 3.0
            elif rank < 20:
                relevance_dict[cid] = 2.0
            else:
                relevance_dict[cid] = 1.0
                
        ivf_ids = [item[0] for item in ivf_results[:5]]
        ndcg = compute_ndcg(ivf_ids, relevance_dict, k=5)
        ndcg_scores.append(ndcg)
        
    return {
        "scale": scale,
        "flat_build_ms": flat_build_time,
        "ivf_build_ms": ivf_build_time,
        "flat_search_avg_ms": np.mean(flat_latencies),
        "ivf_search_avg_ms": np.mean(ivf_latencies),
        "rerank_avg_ms": np.mean(rerank_latencies),
        "ndcg_avg": np.mean(ndcg_scores),
        "ivf_type": ivf_index.index_type
    }

if __name__ == "__main__":
    scales = [100, 1000, 10000]
    results = []
    
    for s in scales:
        res = run_scale_benchmark(s)
        results.append(res)
        
    # Generate Markdown report
    print("\n\n" + "="*50)
    print("AI REWARDS CONCIERGE - SEARCH PERFORMANCE REPORT")
    print("="*50)
    
    report_lines = [
        "# AI Rewards Concierge - FAISS & Re-ranking Benchmark Report",
        "",
        "| Scale (Cards) | Index Type | Index Build Time (ms) | Avg Query Search Latency (ms) | Avg Re-ranking & Rules Overhead (ms) | Total Pipeline Latency (ms) | Recall Quality (NDCG@5 vs Flat) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for r in results:
        scale = r["scale"]
        flat_search = r["flat_search_avg_ms"]
        ivf_search = r["ivf_search_avg_ms"]
        rerank = r["rerank_avg_ms"]
        ndcg = r["ndcg_avg"]
        
        # Report Flat results
        report_lines.append(
            f"| {scale:,} | **Flat** | {r['flat_build_ms']:.2f} | {flat_search:.4f} | {rerank:.4f} | {flat_search + rerank:.4f} | 1.0000 (Exact) |"
        )
        
        # Report IVF results
        idx_type = r["ivf_type"]
        if idx_type == "Flat":
            idx_type = "Flat (Fallback)"
        report_lines.append(
            f"| {scale:,} | **{idx_type}** | {r['ivf_build_ms']:.2f} | {ivf_search:.4f} | {rerank:.4f} | {ivf_search + rerank:.4f} | {ndcg:.4f} |"
        )
        
    report = "\n".join(report_lines)
    print(report)
    
    # Save to file
    with open("benchmarks/performance_report.md", "w") as f:
        f.write(report)
    print("\nSaved report to benchmarks/performance_report.md")
