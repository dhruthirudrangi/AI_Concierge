# 📊 Project Summary - What's Been Built

## 🎯 Project Purpose
An **AI-Powered Credit Card Recommendation Engine** that combines eligibility filtering, spending profile matching, and semantic AI to recommend the best credit cards for users.

---

## ✅ Core Components Implemented

### 1. **FastAPI Backend** (`app/main.py`)
- RESTful API server with automatic documentation
- Pre-loads Sentence Transformer model on startup to avoid cold starts
- Includes both recommendation and benchmarking endpoints

### 2. **MongoDB Database Layer** (`app/db/mongo.py`)
- Stores credit card data with details and pre-computed embeddings
- Collection: `cards` in database `credit_card_recommendation`
- Stores 384-dimensional embeddings for semantic search

### 3. **Eligibility Service** (`app/services/eligibility_service.py`)
```python
• filter_eligible_cards(min_balance, region)
  └─ Filters by: active status ✓, region ✓, balance requirement ✓
  
• calculate_card_score(card, spending_categories)
  └─ Matches user spending to card reward categories
  └─ Formula: For each match: score += amount × 0.0001
```

### 4. **Three Semantic Matching Methods** (`app/services/`)

#### A. TF-IDF Method (Keyword-based)
- File: `semantic_service.py::get_tfidf_scores()`
- Tokenizes card descriptions
- Computes cosine similarity with user preference text
- **Speed: FASTEST ⚡** 
- **Use case:** Quick keyword matching

#### B. Sentence Transformer (Deep Learning)
- File: `semantic_service.py::get_transformer_scores()`
- Uses "all-MiniLM-L6-v2" model (384-dim embeddings)
- Pre-computed at seed time and cached in DB
- **Speed: FAST**
- **Use case:** Best semantic understanding ⭐

#### C. FAISS (Vector Search)
- File: `faiss_service.py::get_faiss_scores()`
- Builds dynamic FAISS IndexFlatIP for each query
- Normalizes vectors to compute cosine similarity via inner product
- **Speed: FASTEST for large catalogs 🚀**
- **Use case:** 100+ card databases

### 5. **Hybrid Recommendation Engine** (`app/services/hybrid_service.py`)
```
compute_hybrid_recommendations():
  1. Calculate spending category match scores
  2. Calculate semantic preference match scores
  3. Normalize both to [0, 1]
  4. Combine: final_score = (w_semantic × semantic) + (w_spending × spending)
  5. Sort by final_score descending
  6. Return with natural language explanations
```

**Adjustable Weights:**
- `weight_semantic` (0-1): Importance of preference text matching
- `weight_spending` (0-1): Importance of spending profile matching
- Sum doesn't need to equal 1.0 (auto-normalized)

### 6. **Evaluation Service** (`app/services/evaluation_service.py`)
Computes academic metrics for ranking quality:

- **Precision@K** - % of relevant items in top K results
- **MRR** - Mean Reciprocal Rank (rank of first relevant item)
- **NDCG@K** - Normalized Discounted Cumulative Gain

Uses benchmark dataset with 6 queries + ground truth relevant cards

### 7. **API Endpoints** (`app/routers/`)

#### Recommendation Endpoint
```
POST /recommend
├─ Input: RecommendRequest with:
│  ├─ user_id: string
│  ├─ spending_categories: {category: amount}
│  ├─ region: string (e.g., "India", "USA")
│  ├─ min_balance: float
│  ├─ preference_text: optional text describing preferences
│  ├─ semantic_method: "tfidf" | "sentence_transformer" | "faiss"
│  ├─ weight_semantic: 0.0-1.0
│  └─ weight_spending: 0.0-1.0
│
└─ Output: RecommendResponse
   └─ recommendations[] with:
      ├─ card_id, name
      ├─ final_score: 0-1
      ├─ spending_score: raw calculation
      ├─ semantic_score: similarity 0-1
      └─ match_reason: human-readable explanation
```

#### Evaluation Endpoint
```
POST /evaluate?k=3
└─ Returns: Precision@K, MRR, NDCG@K for all 3 methods
```

#### Benchmark Endpoint
```
POST /benchmark?num_queries=50
└─ Returns: Average, p50, p95 latency in milliseconds
```

### 8. **Database Seeding** (`seed.py`)
Pre-loads 7 demo credit cards:

| Card | Region | Min Balance | Categories |
|------|--------|-------------|-----------|
| CARD001 - Premium Cashback | India | ₹10K | dining, shopping |
| CARD002 - Travel Rewards | India | ₹50K | travel, flights |
| CARD003 - Fuel Saver | India | ₹5K | fuel, transport |
| CARD004 - Premium Dining | India | ₹100K | dining, entertainment |
| CARD005 - Supercharger Shopping | India | ₹15K | shopping, electronics |
| CARD006 - Zero Fee | India | ₹0 | utility, groceries |
| CARD007 - Globetrotter Luxury | USA | ₹150K | travel, dining |

### 9. **Comprehensive Tests** (`tests/test_recommend.py`)

```
✓ test_home_endpoint() - API is running
✓ test_tfidf_similarity() - TF-IDF ranking works
✓ test_sentence_transformer_similarity() - Semantic matching works
✓ test_faiss_similarity() - Vector search works
✓ test_hybrid_recommendation() - Hybrid engine combines scores correctly
✓ test_academic_metrics() - Precision@K, MRR, NDCG formulas correct
✓ test_recommend_api() - End-to-end API test
✓ test_evaluate_api() - Metrics computation works
```

### 10. **Pydantic Models** (`app/models/schemas.py`)
- `RecommendRequest` - Input validation
- `CardResponse` - Recommendation output
- `RecommendResponse` - List of recommendations
- `MetricScore` - Evaluation results
- `LatencyMetrics` - Benchmarking results

---

## 🧪 Testing Infrastructure

### Test Coverage
- Unit tests for each semantic method
- Integration tests for hybrid recommendations
- End-to-end API tests
- Academic metrics validation
- 8 different test scenarios

### Test Runners
1. **Interactive Test Menu** - `python run_tests.py`
2. **Pytest CLI** - `pytest tests/test_recommend.py -v`
3. **Quick Smoke Test** - `python run_tests.py --quick`

### Test Execution
```bash
# All tests
pytest tests/test_recommend.py -v

# Specific test
pytest tests/test_recommend.py::test_hybrid_recommendation -v

# With output
pytest tests/test_recommend.py -v -s
```

---

## 💾 How to Add Cards Dynamically

### 5 Methods Available

#### Method 1: Direct Python Script (Recommended)
```python
from manage_cards import add_single_card

add_single_card(
    card_id="CARD008",
    name="Student Card",
    description="...",
    min_balance_required=1000,
    region="India",
    preferred_categories=["education", "books"]
)
```

#### Method 2: Batch Add from File
```python
from manage_cards import add_multiple_cards

cards = [
    {"card_id": "CARD009", "name": "Gym Card", ...},
    {"card_id": "CARD010", "name": "Pet Card", ...}
]
result = add_multiple_cards(cards)
```

#### Method 3: Update Existing Card
```python
from manage_cards import update_card

update_card("CARD001", {
    "name": "New Name",
    "min_balance_required": 20000
})
```

#### Method 4: Delete Card
```python
from manage_cards import delete_card

delete_card("CARD001")
```

#### Method 5: Management Demo
```bash
python manage_cards.py
# Interactive demo with examples
```

### Key Features of Card Addition
- ✅ Auto-generates Sentence Transformer embeddings
- ✅ Validates card uniqueness
- ✅ Stores embeddings for semantic search
- ✅ Supports batch operations
- ✅ Easy to integrate with web interface

---

## 🚀 How to Use the System

### Step 1: Start Services
```bash
# Terminal 1: Start MongoDB (if not running)
docker run -d -p 27017:27017 mongo:latest

# Terminal 2: Seed database
python seed.py

# Terminal 3: Start API
uvicorn app.main:app --reload
```

### Step 2: Get Recommendations
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "U001",
    "spending_categories": {"shopping": 5000},
    "region": "India",
    "min_balance": 15000,
    "preference_text": "I want cashback on shopping",
    "weight_semantic": 0.5,
    "weight_spending": 0.5
  }'
```

### Step 3: Evaluate & Benchmark
```bash
# Check recommendation quality
curl -X POST http://localhost:8000/evaluate?k=3

# Measure performance
curl -X POST http://localhost:8000/benchmark?num_queries=50
```

---

## 📊 Architecture Diagram

```
User Request
    ↓
API Endpoint (/recommend)
    ↓
├─ Eligibility Service
│  └─ Filter by: region, balance, active status
│     ↓
├─ Spending Service
│  └─ Calculate spending category matches
│     ↓
├─ Semantic Service (choose one: TF-IDF / Transformer / FAISS)
│  ├─ TF-IDF: Fast keyword matching
│  ├─ Sentence Transformer: Semantic understanding
│  └─ FAISS: Vector similarity search
│     ↓
├─ Hybrid Engine
│  └─ Combine spending + semantic with weights
│     ↓
└─ Sort & Explain
   ├─ Sort by final_score
   ├─ Generate match_reason
   └─ Return recommendations

MongoDB
├─ Stores 7 demo cards
├─ Pre-computed embeddings (384-dim)
└─ Ready for dynamic additions
```

---

## 📈 Performance Characteristics

| Method | Speed | Accuracy | Memory | Best For |
|--------|-------|----------|--------|----------|
| TF-IDF | ⚡⚡⚡ FASTEST | Good | Low | Keyword matching |
| Sentence Transformer | ⚡⚡ FAST | ⭐⭐⭐ BEST | High | Semantic understanding |
| FAISS | ⚡⚡⚡ FASTEST | ⭐⭐ Excellent | High | Large catalogs (100+) |

---

## 🎓 Academic Metrics Implemented

### Precision@K
Formula: `Relevant_Retrieved / K`
Measures: % of top-K results that are relevant

### Mean Reciprocal Rank
Formula: `1 / rank_of_first_relevant_item`
Measures: How quickly a relevant result appears

### NDCG@K
Formula: `DCG@K / IDCG@K`
Measures: Quality of ranking accounting for position

---

## 📁 File Structure

```
app/
├── main.py                    ← FastAPI app initialization
├── models/schemas.py          ← Request/response models
├── routers/
│   ├── recommend.py           ← /recommend endpoint
│   └── benchmark.py           ← /evaluate & /benchmark
├── services/
│   ├── eligibility_service.py ← Filtering & scoring
│   ├── semantic_service.py    ← TF-IDF & Transformer
│   ├── faiss_service.py       ← FAISS vector search
│   ├── hybrid_service.py      ← Recommendation engine
│   └── evaluation_service.py  ← Academic metrics
└── db/mongo.py                ← Database connection

tests/test_recommend.py        ← All 8 test cases

seed.py                        ← Load demo data
run_tests.py                   ← Test runner
manage_cards.py                ← Add cards dynamically
api_examples.py                ← API testing examples
GUIDE.md                       ← Full documentation
README.md                      ← Quick start
```

---

## 🔄 Data Flow Example

**User Query:**
```json
{
  "user_id": "USER123",
  "spending_categories": {"shopping": 5000, "dining": 3000},
  "region": "India",
  "min_balance": 15000,
  "preference_text": "shopping and cashback",
  "weight_semantic": 0.5,
  "weight_spending": 0.5
}
```

**Processing Pipeline:**

1. **Eligibility Filter**
   - Get all cards from DB
   - Filter: active=true, region="India", min_balance ≤ 15000
   - Result: 5 eligible cards

2. **Spending Score Calculation**
   - CARD001 (shopping category): score = 5000 × 0.0001 = 0.5
   - CARD002 (travel category): score = 0
   - etc.

3. **Semantic Matching** (Transformer)
   - Embed user text: "shopping and cashback"
   - Compare with each card's description embedding
   - Get similarity scores 0-1

4. **Hybrid Combination**
   - Normalize spending scores: 0.5/0.5 = 1.0, 0/0.5 = 0, etc.
   - Combine: final = 0.5 × semantic + 0.5 × normalized_spending

5. **Sort & Format**
   - Sort by final_score descending
   - Generate explanations
   - Return top results

**Response:**
```json
{
  "recommendations": [
    {
      "card_id": "CARD001",
      "name": "Premium Cashback Card",
      "final_score": 0.89,
      "spending_score": 0.5,
      "semantic_score": 0.85,
      "match_reason": "Combined Score: 0.89 | 50% Semantic (0.85) + 50% Spending (1.0)"
    },
    {...}
  ]
}
```

---

## 🎯 Key Features Implemented

✅ **Hybrid Recommendations** - Combines multiple AI techniques
✅ **Explainability** - Shows why each card was recommended
✅ **Academic Metrics** - Measures recommendation quality
✅ **Performance Benchmarking** - Tracks latency
✅ **Dynamic Card Addition** - Easy to add new cards
✅ **Three Semantic Methods** - Choose speed vs accuracy
✅ **Adjustable Weights** - Customize recommendations
✅ **Batch Operations** - Add multiple cards at once
✅ **Pre-computation** - Embeddings cached in DB
✅ **Comprehensive Tests** - 8 test scenarios

---

## 🚀 Production Ready Features

✓ Error handling
✓ Input validation with Pydantic
✓ Database indexing support
✓ Model pre-loading to avoid cold starts
✓ Lazy loading for large datasets
✓ Type hints throughout
✓ RESTful API design
✓ Async/await ready architecture
✓ Modular service design
✓ Easy to extend and customize

---

## 📚 Documentation Provided

1. **GUIDE.md** (200+ lines)
   - Complete architecture
   - Service explanations
   - All 5 methods to add cards
   - Example usage flows
   - Performance tips

2. **README.md** (Quick Start)
   - Prerequisites
   - Setup steps
   - Test commands
   - Utility scripts
   - Troubleshooting

3. **api_examples.py** (Interactive)
   - 7 example endpoints
   - CURL commands
   - Python examples

4. **manage_cards.py** (Interactive)
   - Add single/batch cards
   - Update cards
   - Delete cards
   - Search cards
   - List all cards

5. **run_tests.py** (Interactive)
   - 13 different test options
   - Smoke tests
   - Individual test selection

---

## 🎉 Summary

A production-ready **AI-powered credit card recommendation system** with:

- **7 implemented services** (eligibility, semantic x3, hybrid, evaluation)
- **3 API endpoints** (recommend, evaluate, benchmark)
- **8 comprehensive tests**
- **7 demo credit cards** pre-loaded
- **5 methods to add cards** dynamically
- **3 semantic matching algorithms** (TF-IDF, Transformer, FAISS)
- **Academic evaluation metrics** (Precision@K, MRR, NDCG)
- **Performance benchmarking**
- **Complete documentation**
- **Interactive testing tools**

All components are tested, documented, and ready to use! 🚀
