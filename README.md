# AI Rewards Concierge - Vector Search & Re-ranking Engine

This repository contains the backend search, filtering, and scoring engine for the AI Rewards Concierge. 

Our goal is to solve the **"finding matches efficiently"** problem. This engine connects the AI concierge's conversational understanding with real-world business constraints.

---

## What is Implemented

Our system takes the user's chat message and spending profile, searches through thousands of reward cards, filters them based on rules, and ranks the best ones. Here is how it works:

### 1. Fast Vector Search (FAISS)
* **What it does**: Instead of searching for exact keywords (like "travel"), we represent cards and user queries as mathematical lists of numbers (embeddings) that capture meaning.
* **Why it's useful**: We use **FAISS** (Facebook AI Similarity Search). For small card sets, it does a brute-force search. When scaled up to **10,000 cards**, it uses a clustering technique (Approximate Nearest Neighbors) to search the entire database in **less than 2 milliseconds**. If the database is too small for clustering, it safely falls back to standard exact matching.

### 2. Business Rules Engine
* **What it does**: Vector search only checks for semantic similarity. We apply real-world filters on top of the search:
  * **Points Balance**: Excludes cards where the points required exceed what the user currently has.
  * **Region**: Filters out cards not available in the user's geographic region.
  * **Eligibility Tier**: Checks if the card requires a membership tier (like Gold or Platinum) that the user hasn't unlocked.
  * **Availability**: Ensures the card is active and available.
* **Smart Fallback**: If strict rules block too many cards (e.g. the user has very low points), the engine relaxes the rules and shows near-misses with clear warning labels (e.g. *"Requires Platinum Tier (current: Gold)"*).

### 3. Re-ranking & Explanation Generator
* **What it does**: Combines multiple factors to score cards from 0.0 to 1.0:
  * **Similarity** (60% weight)
  * **Spending Multipliers** (20% weight): If a user spends heavily on Dining, cards with 5x Dining points get boosted.
  * **Feedback Shifts** (20% weight): If a user has liked Travel cards in the past, travel cards get boosted.
  * **Penalties**: Slightly drops scores for cards that failed strict rules.
* **Why it's useful**: It dynamically generates text explaining *why* the card was recommended ("Earns 4.0x on Dining, matching your highest spend category"). This text is sent to the LLM so it can converse naturally with the user.

### 4. Feedback Loop Database (SQLite)
* **What it does**: Tracks whenever a user clicks "like", "dislike", or "apply" on a card.
* **Why it's useful**: It saves interactions in a local database. Likes or application actions raise the user's preference scores for those categories, while dislikes subtract score weight. Explicit dislikes ensure that card will not be recommended again.

---

## 🏛️ Design Decision: Why SQLite instead of MongoDB?

Although Member 1 uses **MongoDB** for the overall project data storage, we chose **SQLite** for Member 2's localized feedback loop and benchmarking due to several engineering benefits:

1. **Local Independence & Testing Isolation**: SQLite runs in-process with Python and stores database tables in a single local file. This allowed us to build, debug, and run automated unit tests and performance benchmarks in a completely self-contained workspace without needing a live connection to a shared MongoDB instance.
2. **Zero Network Latency**: Because SQLite executes inside the app process, there are no TCP connection delays or network roundtrips. This allowed us to measure the *pure algorithm overhead* of our re-ranking engine during benchmarks, proving a total pipeline time under **3 milliseconds** (a network database roundtrip alone often takes 10ms–50ms).
3. **Structured Tabular Logging**: The feedback loop logs simple structured interaction tuples (`user_id`, `card_id`, `action`, `categories`, `timestamp`). A lightweight relational database (SQL) is the perfect fit for storing and executing aggregated mathematical queries on this data (such as calculating category weights).
4. **Seamless Integration**: When integrating with Member 1's backend, MongoDB will serve as the global state (storing card records and persistent user profiles). Member 1's API can fetch the profile from MongoDB and pass the resulting Pydantic schemas directly into our modular `ReRanker` and `BusinessRulesEngine` components without needing any code changes.

---

## Project Structure

* **`app/`** (Core Code):
  * [config.py]: System configuration, scoring weights, and search tuning parameters.
  * [data_store.py]: Models for cards/profiles and mock data generation.
  * [faiss_index.py]: Vector indexing operations (Flat L2 and IVF Flat).
  * [business_rules.py]: Checking point limits, regions, tiers, and fallback rules.
  * [re_ranking.py]: Re-ranking logic, spend multipliers, and explanation generator.
  * [feedback_loop.py]: SQLite tracker for logging like/dislike/apply history.
  * [utils.py]: Evaluation metrics (NDCG and MRR calculations).
* **`tests/`** (Tests):
  * Contains unit test files verifying search indexing, rules, and scoring.
* **`benchmarks/`** (Scale Testing):
  * Scripts to evaluate system latencies and search quality at 100, 1K, and 10K card database scales.
* **`run_demo_scenario.py`**:
  * A command-line script running a complete demo of a user looking for a weekend getaway under 4,200 points.

---

## ⚡ How to Run

Ensure python is installed along with the required libraries:
```bash
pip install faiss-cpu numpy pytest pydantic
```

### 1. Run the Interactive Demo
See the complete step-by-step points check, FAISS search, business filtering, re-ranking, and points execution:
```bash
$env:PYTHONPATH="." ; python run_demo_scenario.py
```

### 2. Run the Benchmarking Suite
To test search and re-ranking speeds at 100, 1,000, and 10,000 card scales:
```bash
$env:PYTHONPATH="." ; python benchmarks/benchmark_faiss.py
```
This prints a markdown performance table and saves a report file to `benchmarks/performance_report.md`.

### 3. Run the Automated Tests
Verify that all mathematical operations and rule engines function properly:
```bash
pytest tests/
```
