import numpy as np
import faiss
from app.services.semantic_service import EmbeddingService


def get_faiss_scores(query: str, cards: list) -> dict:
    """
    Computes semantic similarity scores using a FAISS index built dynamically
    for the given list of eligible cards.
    """
    if not query or not cards:
        return {card["card_id"]: 0.0 for card in cards}

    # 1. Prepare vectors for indexing
    embeddings = []
    card_mapping = []  # Maps index in FAISS to card_id

    for i, card in enumerate(cards):
        emb = card.get("description_embedding")
        if emb is None:
            # Generate dynamically if missing
            emb = EmbeddingService.encode(card.get("description", "")).tolist()
        
        embeddings.append(emb)
        card_mapping.append(card["card_id"])

    # Convert to float32 numpy array
    xb = np.array(embeddings, dtype=np.float32)
    embedding_dim = xb.shape[1] if len(xb.shape) > 1 else 384

    # 2. Setup the query vector
    xq = EmbeddingService.encode(query).astype(np.float32).reshape(1, -1)

    # 3. L2 Normalize vectors to compute Cosine Similarity via Inner Product
    faiss.normalize_L2(xb)
    faiss.normalize_L2(xq)

    # 4. Build FAISS IndexFlatIP (Inner Product)
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(xb)

    # 5. Search the index for all eligible cards (k = number of cards)
    k = len(cards)
    distances, indices = index.search(xq, k)

    # 6. Map scores back to card IDs
    scores = {}
    # If index search returns -1 for out-of-bounds, handle it (though here k = len(cards) should be exact)
    for j in range(k):
        idx = indices[0][j]
        if idx != -1:
            card_id = card_mapping[idx]
            # FAISS distance is the cosine similarity because we normalized the vectors
            scores[card_id] = float(distances[0][j])

    # Ensure all cards get a score (if any were skipped or indexed incorrectly)
    for card in cards:
        if card["card_id"] not in scores:
            scores[card["card_id"]] = 0.0

    return scores
