## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+
- MongoDB running on localhost:27017
- pip package manager

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Database
```bash
python seed.py
```
This loads 7 demo credit cards with pre-computed embeddings.

### 3. Run Tests (Optional but Recommended)
```bash
# Interactive test runner
python run_tests.py

# Or run quick smoke test
pytest tests/test_recommend.py -v

# Run specific test
pytest tests/test_recommend.py::test_hybrid_recommendation -v
```

### 4. Start the API Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit: http://localhost:8000/docs (Interactive API docs)

### 5. Test the API
```bash
# Option A: Using Python script
python api_examples.py

# Option B: Using curl
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
```

---

## 📚 Complete Documentation

See [GUIDE.md](GUIDE.md) for comprehensive documentation including:
- ✅ Complete architecture overview
- ✅ What's been built (7 core services)
- ✅ How each service works
- ✅ 8+ testing scenarios
- ✅ 5 methods to add cards dynamically
- ✅ Example usage flows
- ✅ Performance considerations

---

## 🛠️ Utility Scripts

### Test Runner
Interactive menu to run different tests:
```bash
python run_tests.py
```

### Card Management
Add, update, delete cards dynamically:
```bash
python manage_cards.py
```

### API Examples
Test all endpoints with example requests:
```bash
python api_examples.py
```

---

## 📋 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/recommend` | POST | Get card recommendations |
| `/evaluate` | POST | Get academic metrics |
| `/benchmark` | POST | Measure latency |

---

## 💾 Database Structure

**MongoDB Database:** `credit_card_recommendation`  
**Collection:** `cards`

Each card document has:
```json
{
  "card_id": "CARD001",
  "name": "Premium Cashback Card",
  "description": "...",
  "region": "India",
  "min_balance_required": 10000,
  "preferred_categories": ["dining", "shopping"],
  "active": true,
  "description_embedding": [0.123, 0.456, ...]
}
```

---

## 🎯 Next Steps

1. **Read [GUIDE.md](GUIDE.md)** - Full documentation
2. **Run tests** - `python run_tests.py`
3. **Start server** - `uvicorn app.main:app --reload`
4. **Add your cards** - `python manage_cards.py`
5. **Test API** - `python api_examples.py`

---

## ⚡ Performance Tips

- **Fast:** Use TF-IDF for keyword-based matching
- **Accurate:** Use Sentence Transformer for semantic understanding
- **Scalable:** Use FAISS for 100+ card catalogs
- **Cache:** Pre-compute embeddings at seed time (already done!)
- **Monitor:** Check `/benchmark` endpoint for latency metrics

---

## 🐛 Troubleshooting

**MongoDB connection error?**
```bash
# Start MongoDB with Docker
docker run -d -p 27017:27017 mongo:latest
```

**Models not loading?**
```bash
# Pre-load the Sentence Transformer model
python -c "from app.services.semantic_service import EmbeddingService; EmbeddingService.get_model()"
```

**Tests failing?**
```bash
# Make sure database is seeded
python seed.py

# Run verbose tests
pytest tests/test_recommend.py -v -s
```

---

## 📖 Project Structure

```
kobie/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   ├── routers/
│   │   ├── recommend.py           # Recommendation endpoint
│   │   └── benchmark.py           # Evaluation & benchmark endpoints
│   ├── services/
│   │   ├── eligibility_service.py # Card filtering
│   │   ├── hybrid_service.py      # Recommendation engine
│   │   ├── semantic_service.py    # TF-IDF & Sentence Transformer
│   │   ├── faiss_service.py       # Vector search
│   │   └── evaluation_service.py  # Academic metrics
│   └── db/
│       └── mongo.py               # MongoDB connection
├── tests/
│   └── test_recommend.py          # 8 test cases
├── GUIDE.md                       # Complete documentation
├── README.md                      # This file
├── requirements.txt               # Dependencies
├── seed.py                        # Database seeding
├── run_tests.py                   # Test runner
├── manage_cards.py                # Card management
└── api_examples.py                # API examples
```

---

**Happy recommending! 🎉**
