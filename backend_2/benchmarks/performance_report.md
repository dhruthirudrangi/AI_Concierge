# AI Rewards Concierge - FAISS & Re-ranking Benchmark Report

| Scale (Cards) | Index Type | Index Build Time (ms) | Avg Query Search Latency (ms) | Avg Re-ranking & Rules Overhead (ms) | Total Pipeline Latency (ms) | Recall Quality (NDCG@5 vs Flat) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 100 | **Flat** | 1.13 | 0.1889 | 0.5409 | 0.7297 | 1.0000 (Exact) |
| 100 | **Flat (Fallback)** | 0.65 | 0.1701 | 0.5409 | 0.7109 | 1.0000 |
| 1,000 | **Flat** | 10.44 | 0.5744 | 0.5915 | 1.1659 | 1.0000 (Exact) |
| 1,000 | **Flat (Fallback)** | 11.10 | 0.5388 | 0.5915 | 1.1303 | 1.0000 |
| 10,000 | **Flat** | 102.82 | 4.4333 | 0.6658 | 5.0991 | 1.0000 (Exact) |
| 10,000 | **IVF** | 534.18 | 1.8004 | 0.6658 | 2.4662 | 0.7918 |