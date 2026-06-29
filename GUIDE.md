# AI-Powered Credit Card Recommendation System - Complete Guide

## 📋 Project Overview

This is a **FastAPI-based credit card recommendation engine** that uses hybrid AI techniques to recommend credit cards based on:

1. **User Eligibility** - Balance requirements and region availability
2. **Spending Profiles** - Matching user spending patterns to card rewards categories
3. **Semantic Similarity** - Natural language preference matching using three methods

---

## 🏗️ Architecture & What's Been Built

### Core Components

#### 1. **Database Layer** (`app/db/mongo.py`)
- **MongoDB** connection for storing credit card data
- Collections: `cards` - stores card details with embeddings
- Each card stores:
  - `card_id`, `name`, `description`
  - `min_balance_required`, `region`, `active` status
  - `preferred_categories` - spending categories it rewards
  - `description_embedding` - pre-computed Sentence Transformer embeddings

#### 2. **Data Models** (`app/models/schemas.py`)
- `RecommendRequest` - User preference request with weights
- `CardResponse` - Recommendation output with explainability scores
- `RecommendResponse` - List of recommendations

#### 3. **Services Layer**

##### a) **Eligibility Service** (`app/services/eligibility_service.py`)
```
✓ filter_eligible_cards(min_balance, region)
  - Filters cards by: active status, region match, balance requirements
  - Returns list of eligible cards

✓ calculate_card_score(card, spending_categories)
  - Calculates spending profile match score
  - Formula: For each spending category match, add (amount × 0.0001)
```

##### b) **Semantic Similarity Services**

###### **TF-IDF Method** (`app/services/semantic_service.py`)
```
✓ get_tfidf_scores(query, cards)
  - Tokenizes card descriptions using TF-IDF vectorizer
  - Computes cosine similarity with user preference text
  - Returns dictionary: {card_id: similarity_score}
  - Speed: FASTEST ⚡
  - Accuracy: Good for keyword matching
```

###### **Sentence Transformer Method** (Deep Learning)
```
✓ get_transformer_scores(query, cards)
  - Uses "all-MiniLM-L6-v2" model (384-dim embeddings)
  - Pre-computes embeddings at seed time and stores in MongoDB
  - Computes normalized cosine similarity
  - Speed: FAST
  - Accuracy: Best semantic understanding ⭐
```

###### **FAISS Method** (Vector Search)
```
✓ get_faiss_scores(query, cards)
  - Builds dynamic FAISS IndexFlatIP for each query
  - Normalizes vectors to convert inner product → cosine similarity
  - Speed: FASTEST for large datasets 🚀
  - Accuracy: Excellent performance with speed
```

##### c) **Hybrid Recommendation Engine** (`app/services/hybrid_service.py`)
```
compute_hybrid_recommendations():
  1. Calculates spending category match scores
  2. Calculates semantic preference match scores
  3. Normalizes both scores to [0, 1]
  4. Combines using weights: final_score = (w_semantic × semantic) + (w_spending × spending)
  5. Sorts cards by final_score descending
  6. Returns CardResponse with explanations
```

##### d) **Evaluation Service** (`app/services/evaluation_service.py`)
```
Academic Metrics (for benchmarking recommendation quality):
  ✓ calculate_precision_at_k() - % of relevant items in top K
  ✓ calculate_reciprocal_rank() - Rank of first relevant item
  ✓ calculate_ndcg_at_k() - Normalized discounted cumulative gain

evaluate_method(method, k) - Evaluates against 6 benchmark queries with ground truth
```

#### 4. **API Endpoints** (`app/routers/`)

##### a) **Recommendation Router** (`app/routers/recommend.py`)
```
POST /recommend
├─ Input: RecommendRequest
│  ├─ user_id
│  ├─ spending_categories: {category: amount}
│  ├─ region
│  ├─ min_balance
│  ├─ preference_text (optional)
│  ├─ semantic_method: "tfidf" | "sentence_transformer" | "faiss"
│  ├─ weight_semantic: 0.0-1.0 (default 0.5)
│  └─ weight_spending: 0.0-1.0 (default 0.5)
│
└─ Output: RecommendResponse
   └─ recommendations[] with:
      ├─ card_id, name
      ├─ final_score (0-1)
      ├─ spending_score (raw score)
      ├─ semantic_score (raw score)
      └─ match_reason (natural language explanation)
```

##### b) **Benchmark Router** (`app/routers/benchmark.py`)
```
POST /evaluate?k=3
└─ Returns academic metrics (Precision@K, MRR, NDCG@K) for all 3 methods

POST /benchmark?num_queries=50
└─ Measures latency: avg, p50, p95 in milliseconds for all 3 methods
```

#### 5. **Seeding** (`seed.py`)
- Pre-loads 7 demo credit cards into MongoDB
- Pre-computes Sentence Transformer embeddings
- Cards span multiple regions, balance tiers, and spending categories

---

## 🧪 How to Test the Project

### Step 1: Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure MongoDB is running (default: localhost:27017)
# Windows: Use MongoDB Community or Docker
docker run -d -p 27017:27017 mongo:latest
```

### Step 2: Seed the Database
```bash
python seed.py
```
Output: 7 credit cards loaded with embeddings

### Step 3: Run Tests
```bash
# Run all tests
pytest tests/test_recommend.py -v

# Run specific test
pytest tests/test_recommend.py::test_hybrid_recommendation -v

# Run with output
pytest tests/test_recommend.py -v -s
```

### Step 4: Test Cases Explained

```python
✓ test_home_endpoint()
  - Verifies API is running
  - Tests GET /

✓ test_tfidf_similarity()
  - Tests TF-IDF ranking
  - Expects: "I want a shopping card" ranks CARD_T1 (cashback) > CARD_T2 (travel)

✓ test_sentence_transformer_similarity()
  - Tests Sentence Transformer semantic understanding
  - Expects: "I love travelling and flights" ranks CARD_T2 (travel) > CARD_T1 (cashback)

✓ test_faiss_similarity()
  - Tests FAISS vector search
  - Expects: Same ranking as Sentence Transformer

✓ test_hybrid_recommendation()
  - Tests 100% spending weight: Ranks by category match
  - Tests 100% semantic weight: Ranks by preference text similarity

✓ test_academic_metrics()
  - Tests Precision@K, Reciprocal Rank, NDCG@K calculations
  - Validates metric formulas

✓ test_recommend_api()
  - End-to-end API test
  - Validates response structure and explainability fields

✓ test_evaluate_api()
  - Tests academic metrics computation
  - Ensures all 3 methods return results
```

### Step 5: Run the Server
```bash
uvicorn app.main:main --reload --host 0.0.0.0 --port 8000
```

Then test via curl:
```bash
# Test home
curl http://localhost:8000/

# Test recommendation
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "U001",
    "spending_categories": {"shopping": 5000, "dining": 3000},
    "region": "India",
    "min_balance": 15000,
    "preference_text": "shopping and cashback",
    "semantic_method": "sentence_transformer",
    "weight_semantic": 0.5,
    "weight_spending": 0.5
  }'

# Test evaluation metrics
curl -X POST http://localhost:8000/evaluate?k=3

# Test latency benchmarks
curl -X POST http://localhost:8000/benchmark?num_queries=50
```

---

## ➕ How to Dynamically Add Cards

### Method 1: Add Cards to MongoDB Directly

```python
from app.db.mongo import cards_collection
from app.services.semantic_service import EmbeddingService
import numpy as np

# Initialize the model (done at startup automatically)
model = EmbeddingService.get_model()

# Define new card(s)
new_cards = [
    {
        "card_id": "CARD008",
        "name": "Student Rewards Card",
        "min_balance_required": 1000,
        "region": "India",
        "active": True,
        "preferred_categories": ["education", "books", "shopping"],
        "description": "Special student card with discounts on educational materials, books, online courses, and college canteen purchases."
    },
    {
        "card_id": "CARD009",
        "name": "Crypto Enthusiast Card",
        "min_balance_required": 50000,
        "region": "USA",
        "active": True,
        "preferred_categories": ["crypto", "payments", "digital"],
        "description": "Rewards on cryptocurrency purchases, digital payments, and fintech app transactions. Perfect for modern investors."
    }
]

# Generate embeddings
for card in new_cards:
    print(f"Generating embedding for: {card['name']}")
    embedding = model.encode(card["description"])
    card["description_embedding"] = embedding.tolist()

# Insert into MongoDB
result = cards_collection.insert_many(new_cards)
print(f"Added {len(result.inserted_ids)} cards: {result.inserted_ids}")
```

### Method 2: Create a Dynamic Add-Card Endpoint

```python
# Add this to app/routers/recommend.py

from fastapi import HTTPException

@router.post("/add-card")
def add_credit_card(card_data: dict):
    """
    Dynamic endpoint to add a new credit card.
    
    Request body:
    {
        "card_id": "CARD010",
        "name": "New Card Name",
        "min_balance_required": 5000,
        "region": "India",
        "preferred_categories": ["shopping", "dining"],
        "description": "Detailed card description..."
    }
    """
    # Validate required fields
    required_fields = ["card_id", "name", "min_balance_required", "region", "preferred_categories", "description"]
    for field in required_fields:
        if field not in card_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    # Check if card_id already exists
    existing = cards_collection.find_one({"card_id": card_data["card_id"]})
    if existing:
        raise HTTPException(status_code=409, detail=f"Card {card_data['card_id']} already exists")
    
    # Set default active status
    if "active" not in card_data:
        card_data["active"] = True
    
    # Generate embedding
    embedding = EmbeddingService.encode(card_data["description"])
    card_data["description_embedding"] = embedding.tolist()
    
    # Insert into MongoDB
    result = cards_collection.insert_one(card_data)
    
    return {
        "status": "success",
        "card_id": card_data["card_id"],
        "inserted_id": str(result.inserted_id),
        "message": f"Card '{card_data['name']}' added successfully!"
    }
```

Then use it:
```bash
curl -X POST http://localhost:8000/add-card \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "CARD010",
    "name": "Gym & Wellness Card",
    "min_balance_required": 5000,
    "region": "India",
    "active": true,
    "preferred_categories": ["fitness", "health", "wellness"],
    "description": "Get rewards on gym memberships, yoga classes, health insurance, and wellness app subscriptions."
  }'
```

### Method 3: Batch Add Cards (CSV/JSON File)

```python
import json

def add_cards_from_file(file_path: str):
    """Load cards from JSON file and insert into MongoDB"""
    with open(file_path, 'r') as f:
        cards = json.load(f)
    
    # Generate embeddings
    for card in cards:
        embedding = EmbeddingService.encode(card["description"])
        card["description_embedding"] = embedding.tolist()
    
    # Insert all
    result = cards_collection.insert_many(cards)
    print(f"Added {len(result.inserted_ids)} cards from {file_path}")
    return result.inserted_ids

# Usage:
# create a file: new_cards.json
# add_cards_from_file("new_cards.json")
```

Example `new_cards.json`:
```json
[
  {
    "card_id": "CARD011",
    "name": "Green Energy Card",
    "min_balance_required": 10000,
    "region": "India",
    "active": true,
    "preferred_categories": ["eco", "electric", "sustainability"],
    "description": "Support green living with rewards on electric vehicle charging, renewable energy investments, and eco-friendly purchases."
  },
  {
    "card_id": "CARD012",
    "name": "Pet Lover Card",
    "min_balance_required": 5000,
    "region": "India",
    "active": true,
    "preferred_categories": ["pets", "animals", "healthcare"],
    "description": "Perfect for pet owners. Get cashback on pet food, vet services, pet insurance, and pet grooming."
  }
]
```

### Method 4: Update Existing Card

```python
def update_card(card_id: str, updates: dict):
    """Update an existing card"""
    # If description changed, regenerate embedding
    if "description" in updates:
        embedding = EmbeddingService.encode(updates["description"])
        updates["description_embedding"] = embedding.tolist()
    
    result = cards_collection.update_one(
        {"card_id": card_id},
        {"$set": updates}
    )
    
    if result.matched_count == 0:
        return {"error": f"Card {card_id} not found"}
    
    return {
        "status": "success",
        "card_id": card_id,
        "modified_count": result.modified_count
    }

# Usage:
update_card("CARD001", {
    "name": "Premium Cashback Card (Updated)",
    "description": "New description..."
})
```

### Method 5: Delete Card

```python
def delete_card(card_id: str):
    """Delete a card from MongoDB"""
    result = cards_collection.delete_one({"card_id": card_id})
    
    if result.deleted_count == 0:
        return {"error": f"Card {card_id} not found"}
    
    return {
        "status": "success",
        "card_id": card_id,
        "deleted_count": result.deleted_count
    }

# Usage:
delete_card("CARD001")
```

---

## 🧬 Current Seed Data (7 Cards)

| Card ID | Name | Region | Min Balance | Categories |
|---------|------|--------|------------|------------|
| CARD001 | Premium Cashback Card | India | ₹10,000 | dining, shopping |
| CARD002 | Travel Rewards Card | India | ₹50,000 | travel, flights |
| CARD003 | Fuel Saver Card | India | ₹5,000 | fuel, transport |
| CARD004 | Premium Dining & Lifestyle Card | India | ₹100,000 | dining, entertainment |
| CARD005 | Supercharger Shopping Card | India | ₹15,000 | shopping, electronics |
| CARD006 | Basic Zero Fee Card | India | ₹0 | utility, groceries |
| CARD007 | Globetrotter Luxury Card | USA | ₹150,000 | travel, dining |

---

## 📊 Example Usage Flow

### Scenario: Recommend cards for a travel enthusiast

**Request:**
```json
{
  "user_id": "USER123",
  "spending_categories": {
    "travel": 50000,
    "flights": 30000,
    "dining": 10000
  },
  "region": "India",
  "min_balance": 75000,
  "preference_text": "I travel frequently, love airport lounges, and want flight discounts",
  "semantic_method": "sentence_transformer",
  "weight_semantic": 0.6,
  "weight_spending": 0.4
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "card_id": "CARD002",
      "name": "Travel Rewards Card",
      "final_score": 0.9450,
      "spending_score": 0.8,
      "semantic_score": 0.95,
      "match_reason": "Combined Score: 0.95 | 60% Semantic Match (score: 0.95) + 40% Spending Profile Match (score: 0.8, normalized: 1.0)"
    },
    {
      "card_id": "CARD001",
      "name": "Premium Cashback Card",
      "final_score": 0.3200,
      "spending_score": 0.1,
      "semantic_score": 0.32,
      "match_reason": "Combined Score: 0.32 | 60% Semantic Match (score: 0.32) + 40% Spending Profile Match (score: 0.1, normalized: 0.125)"
    }
  ]
}
```

---

## 🎯 Weights Explanation

The hybrid system uses two adjustable weights:

**weight_semantic (0-1):** How much to value natural language preference similarity
**weight_spending (0-1):** How much to value spending profile match

Common scenarios:
- **100% Semantic (1.0, 0.0):** User has specific preferences, little spending data
- **100% Spending (0.0, 1.0):** User wants pure category matching, no preference text
- **Balanced (0.5, 0.5):** Default - both factors equally important

---

## 🚀 Next Steps to Extend

1. **Add User Profile Service** - Store user preferences and historical data
2. **Add Credit Scoring** - Integrate with credit rating agencies
3. **Add Real-time Offers** - Push personalized card offers
4. **Add Feedback Loop** - Track which recommendations users accept and improve model
5. **Add Analytics Dashboard** - Visualize recommendation quality metrics
6. **Add A/B Testing Framework** - Compare different recommendation strategies
7. **Add Caching Layer** - Cache embeddings and results for performance
8. **Add Rate Limiting** - Prevent API abuse
9. **Add Authentication** - Secure the endpoints with JWT/OAuth
10. **Deploy to Cloud** - AWS SageMaker, GCP Vertex AI, or Azure ML

---

## 📝 Notes

- **Embeddings:** All embeddings use the "all-MiniLM-L6-v2" model (384 dimensions)
- **Database:** MongoDB stores card data and pre-computed embeddings
- **Cold Start:** First API call pre-loads the Sentence Transformer model (~300MB)
- **Performance:** FAISS is fastest for large card catalogs (100+)
- **Accuracy:** Sentence Transformer usually provides best semantic understanding
- **Trade-off:** TF-IDF is lightweight, good for deployment with constraints
