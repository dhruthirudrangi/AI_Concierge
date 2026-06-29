#!/usr/bin/env python3
"""
Test Runner Script
Convenient ways to run tests for the credit card recommendation system
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and display results"""
    print(f"\n{'='*70}")
    if description:
        print(f"🔧 {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Main test runner menu"""
    
    print("\n" + "="*70)
    print("📋 CREDIT CARD RECOMMENDATION SYSTEM - TEST RUNNER")
    print("="*70)
    print("\nAvailable test options:\n")
    
    options = {
        "1": {
            "name": "Run all tests",
            "cmd": "pytest tests/test_recommend.py -v"
        },
        "2": {
            "name": "Run all tests with detailed output",
            "cmd": "pytest tests/test_recommend.py -v -s"
        },
        "3": {
            "name": "Test home endpoint",
            "cmd": "pytest tests/test_recommend.py::test_home_endpoint -v -s"
        },
        "4": {
            "name": "Test TF-IDF similarity",
            "cmd": "pytest tests/test_recommend.py::test_tfidf_similarity -v -s"
        },
        "5": {
            "name": "Test Sentence Transformer similarity",
            "cmd": "pytest tests/test_recommend.py::test_sentence_transformer_similarity -v -s"
        },
        "6": {
            "name": "Test FAISS similarity",
            "cmd": "pytest tests/test_recommend.py::test_faiss_similarity -v -s"
        },
        "7": {
            "name": "Test hybrid recommendation engine",
            "cmd": "pytest tests/test_recommend.py::test_hybrid_recommendation -v -s"
        },
        "8": {
            "name": "Test academic metrics (Precision@K, MRR, NDCG)",
            "cmd": "pytest tests/test_recommend.py::test_academic_metrics -v -s"
        },
        "9": {
            "name": "Test recommend API endpoint",
            "cmd": "pytest tests/test_recommend.py::test_recommend_api -v -s"
        },
        "10": {
            "name": "Test evaluation API endpoint",
            "cmd": "pytest tests/test_recommend.py::test_evaluate_api -v -s"
        },
        "11": {
            "name": "Seed database with cards",
            "cmd": "python seed.py"
        },
        "12": {
            "name": "Run interactive card management demo",
            "cmd": "python manage_cards.py"
        },
        "13": {
            "name": "Start FastAPI server (http://localhost:8000)",
            "cmd": "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        },
        "0": {
            "name": "Exit",
            "cmd": None
        }
    }
    
    for key, option in options.items():
        print(f"  [{key}] {option['name']}")
    
    print("\n" + "-"*70)
    
    while True:
        try:
            choice = input("\n👉 Select option (0-13): ").strip()
            
            if choice not in options:
                print("❌ Invalid option. Please try again.")
                continue
            
            if choice == "0":
                print("\n👋 Goodbye!")
                sys.exit(0)
            
            option = options[choice]
            if option["cmd"]:
                success = run_command(option["cmd"], option["name"])
                if not success:
                    print(f"\n⚠️  Command failed with exit code")
            
            again = input("\n🔄 Run another test? (y/n): ").strip().lower()
            if again != 'y':
                print("\n👋 Goodbye!")
                sys.exit(0)
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


def quick_test():
    """Run quick smoke test"""
    print("\n" + "="*70)
    print("🚀 QUICK SMOKE TEST")
    print("="*70)
    
    tests = [
        ("Home endpoint", "pytest tests/test_recommend.py::test_home_endpoint -v"),
        ("TF-IDF", "pytest tests/test_recommend.py::test_tfidf_similarity -v"),
        ("Sentence Transformer", "pytest tests/test_recommend.py::test_sentence_transformer_similarity -v"),
        ("Hybrid recommendation", "pytest tests/test_recommend.py::test_hybrid_recommendation -v"),
        ("Academic metrics", "pytest tests/test_recommend.py::test_academic_metrics -v"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, cmd in tests:
        print(f"\n▶️  {test_name}...", end=" ")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
            failed += 1
    
    print("\n" + "="*70)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("\n❌ pytest not installed!")
        print("Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if running with --quick flag
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = quick_test()
        sys.exit(0 if success else 1)
    
    # Run interactive menu
    main()
