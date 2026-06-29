import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            print("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
            # Using CPU for local execution speed and memory limits
            cls._model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        return cls._model

    @classmethod
    def encode(cls, text: str) -> np.ndarray:
        model = cls.get_model()
        return model.encode(text, convert_to_numpy=True)


def get_tfidf_scores(query: str, cards: list) -> dict:
    """
    Computes cosine similarity using TF-IDF vectors.
    """
    if not query or not cards:
        return {card["card_id"]: 0.0 for card in cards}

    descriptions = [card.get("description", "") for card in cards]
    
    # Simple check if descriptions are empty or all blank
    if not any(descriptions):
        return {card["card_id"]: 0.0 for card in cards}

    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        query_vector = vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        return {cards[i]["card_id"]: float(similarities[i]) for i in range(len(cards))}
    except ValueError:
        # Fallback if vocabulary is empty
        return {card["card_id"]: 0.0 for card in cards}


def get_transformer_scores(query: str, cards: list) -> dict:
    """
    Computes cosine similarity using Sentence Transformer embeddings.
    """
    if not query or not cards:
        return {card["card_id"]: 0.0 for card in cards}

    query_embedding = EmbeddingService.encode(query)
    query_norm = np.linalg.norm(query_embedding)

    scores = {}
    for card in cards:
        emb = card.get("description_embedding")
        if emb is None:
            # Fallback if card embedding was not pre-computed in DB
            emb = EmbeddingService.encode(card.get("description", "")).tolist()
        
        card_emb = np.array(emb, dtype=np.float32)
        card_norm = np.linalg.norm(card_emb)

        if query_norm > 0 and card_norm > 0:
            similarity = np.dot(query_embedding, card_emb) / (query_norm * card_norm)
        else:
            similarity = 0.0
            
        scores[card["card_id"]] = float(similarity)

    return scores
