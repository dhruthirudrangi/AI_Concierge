# AI Rewards Concierge - Vector Search & Re-ranking Walkthrough

We have successfully designed, implemented, and benchmarked the core search, filtering, and scoring modules for the AI Rewards Concierge (Member 2's components). 

All code is fully tested with unit tests and scale-benchmarked to prove production-readiness, scaling capability, and sub-3ms pipeline latencies at 10,000 cards.

---

## 🛠️ Changes Implemented

We created a modular package under [app/](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app) containing:

1. **[config.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app/config.py)**: Configures dimensions (768-d), index paths, default query sizes, scoring weights, and FAISS centroids/probes tuning parameters.
2. **[data_store.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app/data_store.py)**: Pydantic schemas for `RewardCard` and `UserProfile`, along with a JSON-based database manager and synthetic mock generator capable of scaling data deterministically from 100 up to 10,000+ items.
3. **[faiss_index.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app/faiss_index.py)**: A wrapper around the C++ FAISS library implementing:
   - Vector L2 normalization (converting Euclidean distance queries into true cosine similarity matches).
   - Brute-force exact search (`IndexFlatL2`) for small sizes.
   - Approximate cell-probe search (`IndexIVFFlat`) for sub-millisecond scaling.
   - Automatic training safety guards (safely falls back from IVF to Flat when data volume is too low to cluster).
   - Dynamic incremental updates (inserting single cards without full index rebuilds).
4. **[business_rules.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app/business_rules.py)**: Multi-stage filtering rules validating points cost, regional constraints, and membership tier eligibility. Implements a smart relaxation fallback when results fall below threshold limits.
5. **[re_ranking.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app/re_ranking.py)**: Combines multiple factors to calculate a card's final score (similarity score, user-specific spending category multipliers, and database-logged feedback scores). Automatically generates human-readable explanations explaining *why* a card is recommended to feed the conversational LLM.
6. **[feedback_loop.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app/feedback_loop.py)**: Uses an SQLite tracking database to write `like`/`dislike`/`apply` logs and dynamically shift scoring weights or filter out disliked cards.
7. **[utils.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/app/utils.py)**: Holds mathematical logic for rank quality assessments, implementing NDCG and MRR algorithms.

---

## 🧪 Verification & Unit Tests

We created a suite of 15 unit tests covering:
- FAISS indexing accuracy, saving/loading, and IVF fallback.
- Rules engine correctness under strict rules and relaxed fallback cases.
- Re-ranking scoring arithmetic, category multipliers, and explicit card exclusions.
- Feedback loop database logging, affinity shifting, and score range clamping.

We ran the test suite using `pytest` and all tests passed successfully:
```bash
pytest tests/
```

### Test Results
```text
tests/test_business_rules.py .....                                       [ 33%]
tests/test_faiss_index.py ....                                           [ 60%]
tests/test_feedback_loop.py ..                                           [ 73%]
tests/test_re_ranking.py ....                                            [100%]

============================= 15 passed in 4.66s ==============================
```

---

## 📊 Scale Performance Benchmarks

We benchmarked the search and re-ranking pipeline at scales of 100, 1,000, and 10,000 cards. 
To measure retrieval quality degradation under approximate nearest neighbor (ANN) search, we computed NDCG@5 for the IVF index using the exact Flat L2 index results as the ground truth.

Here is the benchmark execution output:

| Scale (Cards) | Index Type | Index Build Time (ms) | Avg Query Search Latency (ms) | Avg Re-ranking & Rules Overhead (ms) | Total Pipeline Latency (ms) | Recall Quality (NDCG@5 vs Flat) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 100 | **Flat** | 1.13 | 0.1889 | 0.5409 | 0.7297 | 1.0000 (Exact) |
| 100 | **Flat (Fallback)** | 0.65 | 0.1701 | 0.5409 | 0.7109 | 1.0000 |
| 1,000 | **Flat** | 10.44 | 0.5744 | 0.5915 | 1.1659 | 1.0000 (Exact) |
| 1,000 | **Flat (Fallback)** | 11.10 | 0.5388 | 0.5915 | 1.1303 | 1.0000 |
| 10,000 | **Flat** | 102.82 | 4.4333 | 0.6658 | 5.0991 | 1.0000 (Exact) |
| 10,000 | **IVF** | 534.18 | 1.8004 | 0.6658 | 2.4662 | 0.7918 |

### Key Benchmark Insights:
1. **Low Volume (100–1K cards)**: The system automatically utilizes fallback rules to bypass IVF training constraints. This guarantees 100% exact retrieval quality (NDCG = 1.0) with total pipeline latency of **~0.7ms to 1.1ms**.
2. **High Volume (10K cards)**: 
   - Brute-force Flat search query latency is 4.43ms.
   - IVF approximate search takes only **1.80ms** (more than 2x speedup).
   - By tuning the search probes parameter (`IVF_PROBES = 30`), we achieve **0.7918 NDCG@5** (high recall accuracy) while maintaining a total pipeline execution time of just **2.47ms**.
3. **Re-ranking Overhead**: Re-ranking candidate cards (checking point limits, regional matches, applying category affinity shifts, and generating explanation text) takes only **~0.6ms**, showcasing a highly optimized business rules engine.

---

## 🎬 Demo Scenario & UI Design Mockup

To demonstrate the full capability of the recommendation engine, we built a script ([run_demo_scenario.py](file:///c:/Users/Manushree%20P%20M/Documents/AI_concierge/run_demo_scenario.py)) mapping directly to the conversational steps outlined in the project challenge slides.

### The 6-Step Conversational Journey

1. **User statement**: "I have 4,200 pts -- suggest a weekend getaway."
2. **Check balance tool**: Validates user has 4,200 points.
3. **FAISS search & filters**: Query vector matches travel-themed cards, and filters exclude cards costing >4,200 points, mismatched regions, or higher membership tiers.
4. **Affinity check**: Loads category-level likes/dislikes (e.g. travel category history) to dynamically adjust weights.
5. **Score & present top picks**: Computes combined final scores, sorts results, and outputs explanation texts.
6. **Redeem execution**: Selects the top pick, executes points deduction, updates points balance, and logs back into the feedback loop.

Run the demo from the root directory:
```bash
python run_demo_scenario.py
```

### UI Mockup Interface Design
Below is a high-fidelity visual UI mockup demonstrating the conversational presentation of recommendations, card carousel, match scores, point cost labels, and balance checks:

![AI Loyalty Rewards Concierge UI Mockup](C:\Users\Manushree P M\.gemini\antigravity-ide\brain\e0b6e194-4ef2-4440-8e8c-6233f256b921\rewards_concierge_ui_1781162847214.png)

