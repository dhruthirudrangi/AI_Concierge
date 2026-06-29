import time
import numpy as np
from fastapi import APIRouter, Query
from app.models.schemas import (
    EvaluationResponse,
    MetricScore,
    BenchmarkResponse,
    LatencyMetrics,
)
from app.services.evaluation_service import evaluate_method, EVALUATION_DATASET
from app.db.mongo import cards_collection
from app.services.semantic_service import get_tfidf_scores, get_transformer_scores
from app.services.faiss_service import get_faiss_scores

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_endpoints(k: int = Query(default=3, ge=1)):
    """
    Computes academic metrics (Precision@K, MRR, NDCG@K) for all three semantic retrieval methods.
    """
    results = []
    for method in ["tfidf", "sentence_transformer", "faiss"]:
        metrics = evaluate_method(method, k=k)
        results.append(
            MetricScore(
                method=method,
                precision_at_k=metrics["precision_at_k"],
                mrr=metrics["mrr"],
                ndcg=metrics["ndcg"],
            )
        )
    return EvaluationResponse(k=k, results=results)


@router.post("/benchmark", response_model=BenchmarkResponse)
def benchmark_latency(num_queries: int = Query(default=50, ge=1, le=200)):
    """
    Measures the average, p50, and p95 retrieval latency in milliseconds for TF-IDF,
    Sentence Transformers, and FAISS over a given number of benchmark queries.
    """
    cards = list(cards_collection.find({"active": True}))
    if not cards:
        return BenchmarkResponse(num_queries=0, metrics=[])

    # Extract query text to run benchmarks
    queries = [item["query"] for item in EVALUATION_DATASET]

    metrics_list = []
    for method in ["tfidf", "sentence_transformer", "faiss"]:
        latencies = []
        for i in range(num_queries):
            query = queries[i % len(queries)]
            
            # Record start timestamp
            start_time = time.perf_counter()

            if method == "tfidf":
                _ = get_tfidf_scores(query, cards)
            elif method == "faiss":
                _ = get_faiss_scores(query, cards)
            else:
                _ = get_transformer_scores(query, cards)

            # Record end timestamp
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000.0
            latencies.append(latency_ms)

        # Compute statistical percentiles
        avg_latency = float(np.mean(latencies))
        p50_latency = float(np.percentile(latencies, 50))
        p95_latency = float(np.percentile(latencies, 95))

        metrics_list.append(
            LatencyMetrics(
                method=method,
                avg_latency_ms=round(avg_latency, 4),
                p50_latency_ms=round(p50_latency, 4),
                p95_latency_ms=round(p95_latency, 4),
            )
        )

    return BenchmarkResponse(num_queries=num_queries, metrics=metrics_list)
