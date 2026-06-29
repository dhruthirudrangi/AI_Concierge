import os

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# FAISS Configuration
EMBEDDING_DIM = 768            # Dimension of BERT embeddings
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
IVF_CENTROIDS = 100            # Number of clusters for IndexIVFFlat
IVF_PROBES = 30                # Number of clusters to check during query
DEFAULT_RETRIEVAL_K = 50       # Retrieve top 50 matches before filtering

# Business Logic & Re-ranking Settings
MIN_RECOMMENDATIONS = 3        # If recommendations fall below this, relax filters
DEFAULT_RECOMMENDATION_COUNT = 5 # Return top 5-10 cards to the user

# Re-ranking Weights
# FinalScore = w_sim * Similarity + w_multiplier * MultiplierBonus + w_feedback * FeedbackBonus
WEIGHT_SIMILARITY = 0.6
WEIGHT_MULTIPLIER = 0.2
WEIGHT_FEEDBACK = 0.2

# Mock DB paths
CARDS_DB_PATH = os.path.join(DATA_DIR, "cards_db.json")
PROFILES_DB_PATH = os.path.join(DATA_DIR, "profiles_db.json")
FEEDBACK_DB_PATH = os.path.join(DATA_DIR, "feedback_db.sqlite")
