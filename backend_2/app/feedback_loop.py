import sqlite3
import os
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
from .config import FEEDBACK_DB_PATH

class FeedbackLoopTracker:
    def __init__(self, db_path: str = FEEDBACK_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite feedback table if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                card_id TEXT NOT NULL,
                action TEXT NOT NULL,          -- 'like', 'dislike', 'apply'
                categories TEXT NOT NULL,      -- Comma-separated list of categories
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def log_feedback(self, user_id: str, card_id: str, action: str, categories: List[str]):
        """Log a user interaction event."""
        if action not in ("like", "dislike", "apply"):
            raise ValueError("Action must be 'like', 'dislike', or 'apply'")
            
        categories_str = ",".join(categories)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_feedback (user_id, card_id, action, categories)
            VALUES (?, ?, ?, ?)
        """, (user_id, card_id, action, categories_str))
        conn.commit()
        conn.close()
        print(f"Logged feedback: User={user_id}, Card={card_id}, Action={action}")

    def get_user_affinity(self, user_id: str) -> Tuple[Dict[str, float], Set[str]]:
        """
        Retrieve user category affinity weights and set of disliked card IDs.
        Likes add +1.0, applies add +2.0, dislikes subtract -2.0.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT card_id, action, categories FROM user_feedback
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        category_scores: Dict[str, float] = {}
        disliked_cards: Set[str] = set()

        for card_id, action, categories_str in rows:
            # Track disliked card IDs
            if action == "dislike":
                disliked_cards.add(card_id)

            # Accumulate category affinity
            weight = 0.0
            if action == "like":
                weight = 1.0
            elif action == "apply":
                weight = 2.0
            elif action == "dislike":
                weight = -2.0

            if categories_str:
                for cat in categories_str.split(","):
                    cat = cat.strip()
                    if cat:
                        category_scores[cat] = category_scores.get(cat, 0.0) + weight

        # Normalize or squash feedback scores to prevent run-away weights
        # We clamp category affinity adjustments to be within [-5.0, 5.0]
        for cat in category_scores:
            category_scores[cat] = max(-5.0, min(5.0, category_scores[cat]))

        return category_scores, disliked_cards

    def clear_feedback(self, user_id: Optional[str] = None):
        """Helper to reset database for tests."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if user_id:
            cursor.execute("DELETE FROM user_feedback WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("DELETE FROM user_feedback")
        conn.commit()
        conn.close()
