"""
API Usage Examples
Demonstrates how to use the Credit Card Recommendation API
"""

import requests
import json

# Base URL for local development
BASE_URL = "http://localhost:8000"

# ==================== EXAMPLE 1: Basic Recommendation ====================

def example_basic_recommendation():
    """Get card recommendations based on spending profile"""
    
    endpoint = f"{BASE_URL}/recommend"
    
    payload = {
        "user_id": "USER123",
        "spending_categories": {
            "shopping": 5000,
            "dining": 3000,
            "groceries": 2000
        },
        "region": "India",
        "min_balance": 15000,
        "preference_text": "I love shopping and eating out",
        "semantic_method": "sentence_transformer",
        "weight_semantic": 0.5,
        "weight_spending": 0.5
    }
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Recommendation")
    print("="*70)
    print(f"Request: POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


# ==================== EXAMPLE 2: Travel Card Recommendation ====================

def example_travel_recommendation():
    """Get recommendations for a frequent traveler"""
    
    endpoint = f"{BASE_URL}/recommend"
    
    payload = {
        "user_id": "TRAVELER001",
        "spending_categories": {
            "travel": 50000,
            "flights": 30000,
            "hotels": 20000
        },
        "region": "India",
        "min_balance": 100000,
        "preference_text": "I travel frequently, need airport lounge access and flight discounts",
        "semantic_method": "faiss",  # Try FAISS for fast retrieval
        "weight_semantic": 0.7,  # Prioritize semantic matching
        "weight_spending": 0.3
    }
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Travel Card Recommendation")
    print("="*70)
    print(f"Request: POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


# ==================== EXAMPLE 3: Pure Spending Profile ====================

def example_spending_only_recommendation():
    """Get recommendations using only spending profile (no preference text)"""
    
    endpoint = f"{BASE_URL}/recommend"
    
    payload = {
        "user_id": "USER456",
        "spending_categories": {
            "fuel": 10000,
            "transport": 5000
        },
        "region": "India",
        "min_balance": 10000,
        "preference_text": "",  # Empty preference text
        "semantic_method": "sentence_transformer",
        "weight_semantic": 0.0,  # No semantic weight
        "weight_spending": 1.0   # 100% spending-based
    }
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Pure Spending Profile Recommendation")
    print("="*70)
    print(f"Request: POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


# ==================== EXAMPLE 4: Pure Semantic ====================

def example_semantic_only_recommendation():
    """Get recommendations using only semantic preference (no spending data)"""
    
    endpoint = f"{BASE_URL}/recommend"
    
    payload = {
        "user_id": "USER789",
        "spending_categories": {},  # Empty spending
        "region": "India",
        "min_balance": 5000,
        "preference_text": "I want a free card with no annual fees for basic utility payments",
        "semantic_method": "tfidf",  # Fast keyword matching
        "weight_semantic": 1.0,  # 100% semantic
        "weight_spending": 0.0
    }
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Pure Semantic Preference Recommendation")
    print("="*70)
    print(f"Request: POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


# ==================== EXAMPLE 5: Evaluation Metrics ====================

def example_evaluation():
    """Compare recommendation quality across all 3 semantic methods"""
    
    endpoint = f"{BASE_URL}/evaluate"
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Evaluation Metrics (Precision@K, MRR, NDCG@K)")
    print("="*70)
    print(f"Request: POST {endpoint}?k=3")
    print(f"Measuring: Precision@3, MRR, NDCG@3 for all 3 methods\n")
    
    try:
        response = requests.post(f"{endpoint}?k=3")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        print(f"\nAcademic Metrics (k={data['k']}):")
        print("-" * 70)
        for metric in data['results']:
            print(f"\nMethod: {metric['method'].upper()}")
            print(f"  Precision@K: {metric['precision_at_k']:.4f}")
            print(f"  MRR (Mean Reciprocal Rank): {metric['mrr']:.4f}")
            print(f"  NDCG@K: {metric['ndcg']:.4f}")
    except Exception as e:
        print(f"Error: {e}")


# ==================== EXAMPLE 6: Latency Benchmarking ====================

def example_benchmark():
    """Benchmark latency of all 3 semantic methods"""
    
    endpoint = f"{BASE_URL}/benchmark"
    
    print("\n" + "="*70)
    print("EXAMPLE 6: Latency Benchmarking")
    print("="*70)
    print(f"Request: POST {endpoint}?num_queries=50")
    print(f"Measuring: Average, p50, p95 latency in milliseconds\n")
    
    try:
        response = requests.post(f"{endpoint}?num_queries=50")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        print(f"\nLatency Results ({data['num_queries']} queries):")
        print("-" * 70)
        for metric in data['metrics']:
            print(f"\nMethod: {metric['method'].upper()}")
            print(f"  Average: {metric['avg_latency_ms']:.2f} ms")
            print(f"  p50 (Median): {metric['p50_latency_ms']:.2f} ms")
            print(f"  p95: {metric['p95_latency_ms']:.2f} ms")
            
        # Find fastest method
        fastest = min(data['metrics'], key=lambda x: x['avg_latency_ms'])
        print(f"\n🚀 Fastest method: {fastest['method']} ({fastest['avg_latency_ms']:.2f} ms avg)")
    except Exception as e:
        print(f"Error: {e}")


# ==================== EXAMPLE 7: Home Endpoint ====================

def example_home():
    """Check if API is running"""
    
    endpoint = f"{BASE_URL}/"
    
    print("\n" + "="*70)
    print("EXAMPLE 7: Health Check - Home Endpoint")
    print("="*70)
    print(f"Request: GET {endpoint}\n")
    
    try:
        response = requests.get(endpoint)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the server is running: uvicorn app.main:app --reload")


# ==================== CURL EXAMPLES ====================

def print_curl_examples():
    """Print curl command examples for quick testing"""
    
    print("\n" + "="*70)
    print("CURL COMMAND EXAMPLES")
    print("="*70)
    
    examples = [
        {
            "name": "Health Check",
            "cmd": 'curl http://localhost:8000/'
        },
        {
            "name": "Basic Recommendation",
            "cmd": '''curl -X POST http://localhost:8000/recommend \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_id": "USER123",
    "spending_categories": {"shopping": 5000, "dining": 3000},
    "region": "India",
    "min_balance": 15000,
    "preference_text": "shopping and cashback",
    "semantic_method": "sentence_transformer",
    "weight_semantic": 0.5,
    "weight_spending": 0.5
  }' '''
        },
        {
            "name": "Travel Recommendation",
            "cmd": '''curl -X POST http://localhost:8000/recommend \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_id": "TRAVELER001",
    "spending_categories": {"travel": 50000, "flights": 30000},
    "region": "India",
    "min_balance": 100000,
    "preference_text": "frequent travel, airport lounge access, flight discounts",
    "semantic_method": "faiss",
    "weight_semantic": 0.7,
    "weight_spending": 0.3
  }' '''
        },
        {
            "name": "Evaluation Metrics",
            "cmd": 'curl -X POST http://localhost:8000/evaluate?k=3'
        },
        {
            "name": "Benchmark Latency",
            "cmd": 'curl -X POST http://localhost:8000/benchmark?num_queries=50'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}:")
        print("-" * 70)
        print(example['cmd'])


# ==================== MAIN ====================

if __name__ == "__main__":
    
    import sys
    
    print("\n" + "="*70)
    print("💳 CREDIT CARD RECOMMENDATION API - USAGE EXAMPLES")
    print("="*70)
    print("\nMake sure the API is running before executing these examples:")
    print("  $ uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAvailable examples:\n")
    
    examples = {
        "1": ("Basic Recommendation", example_basic_recommendation),
        "2": ("Travel Card Recommendation", example_travel_recommendation),
        "3": ("Spending-Only Recommendation", example_spending_only_recommendation),
        "4": ("Semantic-Only Recommendation", example_semantic_only_recommendation),
        "5": ("Evaluation Metrics", example_evaluation),
        "6": ("Latency Benchmarking", example_benchmark),
        "7": ("Health Check", example_home),
        "8": ("Print CURL Examples", print_curl_examples),
        "9": ("Run All Examples", None),
    }
    
    for key, (name, _) in examples.items():
        print(f"  [{key}] {name}")
    
    print(f"  [0] Exit")
    
    print("\n" + "-"*70)
    
    try:
        choice = input("\n👉 Select example (0-9): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            sys.exit(0)
        elif choice == "9":
            # Run all examples
            example_home()
            example_basic_recommendation()
            example_travel_recommendation()
            example_spending_only_recommendation()
            example_semantic_only_recommendation()
            example_evaluation()
            example_benchmark()
            print_curl_examples()
        elif choice in examples:
            name, func = examples[choice]
            if func:
                func()
        else:
            print("❌ Invalid option")
            
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")
        sys.exit(0)
