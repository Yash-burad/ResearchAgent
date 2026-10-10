import json
import sqlite3
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from research_agent.models.feed import (
    BookmarkItem,
    MissedQuestionItem,
    LearningTelemetryItem,
    RecentSearchItem,
    StockWatchlistItem
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data"

class FeedStore:
    """
    SQLite-backed storage for user feed metadata, bookmarks, candidate missed questions,
    and adaptive learning telemetry.
    """

    def __init__(self, db_path: Optional[str] = None):
        target_dir = Path(db_path).parent if db_path else DEFAULT_DATA_PATH
        target_dir.mkdir(exist_ok=True, parents=True)
        self.db_path = Path(db_path).resolve() if db_path else (DEFAULT_DATA_PATH / "user_profile.db")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Activity Log
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                query_text TEXT NOT NULL,
                run_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_domain_query ON activity_log(domain, query_text);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_created_at ON activity_log(created_at);")

            # 2. Bookmarks
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                item_type TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT DEFAULT '',
                reference_path TEXT NOT NULL UNIQUE,
                external_url TEXT,
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_domain ON bookmarks(domain);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_created ON bookmarks(created_at);")

            # 3. Missed Questions (Stumble Log)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS missed_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                company TEXT,
                what_tripped_me TEXT NOT NULL,
                source TEXT DEFAULT 'manual_entry',
                difficulty TEXT DEFAULT 'Medium',
                mastery_level INTEGER DEFAULT 0,
                review_count INTEGER DEFAULT 0,
                next_review_due TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_missed_due ON missed_questions(next_review_due, mastery_level);")

            # 4. Learning Telemetry
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_slug TEXT NOT NULL,
                card_id TEXT,
                game_type TEXT DEFAULT 'flashcards',
                result TEXT NOT NULL,
                feedback_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_topic ON learning_telemetry(topic_slug, result);")

            # 5. Stock Watchlist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_watchlist (
                ticker TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                current_price REAL,
                dcf_target_price REAL,
                dcf_upside_percent REAL,
                conviction TEXT DEFAULT 'Neutral',
                critic_warning TEXT,
                run_id TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            conn.commit()

    # ================= Activity & Trend Methods =================

    def log_activity(self, domain: str, query_text: str, run_id: Optional[str] = None):
        if not query_text or not query_text.strip():
            return
        clean_text = query_text.strip()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO activity_log (domain, query_text, run_id) VALUES (?, ?, ?)",
                (domain, clean_text, run_id)
            )
            conn.commit()

    def get_recent_searches(self, domain: Optional[str] = None, limit: int = 10) -> List[RecentSearchItem]:
        query = "SELECT query_text, domain, run_id, created_at FROM activity_log"
        params: List[Any] = []
        if domain:
            query += " WHERE domain = ?"
            params.append(domain)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                RecentSearchItem(
                    query_text=r["query_text"],
                    domain=r["domain"],
                    count=1,
                    score=1.0,
                    last_searched=r["created_at"],
                    run_id=r["run_id"]
                )
                for r in rows
            ]

    def get_top_trends(self, domain: Optional[str] = None, limit: int = 6, decay_lambda: float = 0.1) -> List[RecentSearchItem]:
        """
        Calculates recency-decay weighted popularity:
        Score = sum(exp(-decay_lambda * delta_days)) for each occurrence.
        """
        query = "SELECT query_text, domain, run_id, created_at FROM activity_log"
        params: List[Any] = []
        if domain:
            query += " WHERE domain = ?"
            params.append(domain)
        query += " ORDER BY created_at DESC"

        now = datetime.now()
        aggregated: Dict[str, Dict[str, Any]] = {}

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            for r in rows:
                key = r["query_text"]
                try:
                    created = datetime.fromisoformat(r["created_at"])
                except Exception:
                    created = now
                delta_days = max(0.0, (now - created).total_seconds() / 86400.0)
                score_increment = math.exp(-decay_lambda * delta_days)

                if key not in aggregated:
                    aggregated[key] = {
                        "query_text": key,
                        "domain": r["domain"],
                        "count": 0,
                        "score": 0.0,
                        "last_searched": r["created_at"],
                        "run_id": r["run_id"]
                    }
                aggregated[key]["count"] += 1
                aggregated[key]["score"] += score_increment

        sorted_trends = sorted(aggregated.values(), key=lambda x: x["score"], reverse=True)[:limit]
        return [RecentSearchItem(**item) for item in sorted_trends]

    # ================= Bookmark Methods =================

    def add_bookmark(
        self,
        domain: str,
        item_type: str,
        title: str,
        reference_path: str,
        summary: str = "",
        external_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BookmarkItem:
        tags_json = json.dumps(tags or [])
        meta_json = json.dumps(metadata or {})
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO bookmarks (domain, item_type, title, summary, reference_path, external_url, tags, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(reference_path) DO UPDATE SET
                title=excluded.title,
                summary=excluded.summary,
                external_url=excluded.external_url,
                tags=excluded.tags,
                metadata=excluded.metadata;
            """, (domain, item_type, title, summary, reference_path, external_url, tags_json, meta_json, now_str))
            conn.commit()
            
            row = conn.execute("SELECT * FROM bookmarks WHERE reference_path = ?", (reference_path,)).fetchone()
            return self._row_to_bookmark(row)

    def list_bookmarks(self, domain: Optional[str] = None) -> List[BookmarkItem]:
        query = "SELECT * FROM bookmarks"
        params: List[Any] = []
        if domain:
            query += " WHERE domain = ?"
            params.append(domain)
        query += " ORDER BY created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_bookmark(r) for r in rows]

    def delete_bookmark(self, bookmark_id: int) -> bool:
        with self._get_connection() as conn:
            res = conn.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
            conn.commit()
            return res.rowcount > 0

    def is_bookmarked(self, reference_path: str) -> bool:
        with self._get_connection() as conn:
            row = conn.execute("SELECT 1 FROM bookmarks WHERE reference_path = ?", (reference_path,)).fetchone()
            return row is not None

    def _row_to_bookmark(self, r: sqlite3.Row) -> BookmarkItem:
        try:
            tags = json.loads(r["tags"]) if r["tags"] else []
        except Exception:
            tags = []
        try:
            meta = json.loads(r["metadata"]) if r["metadata"] else {}
        except Exception:
            meta = {}
        return BookmarkItem(
            id=r["id"],
            domain=r["domain"],
            item_type=r["item_type"],
            title=r["title"],
            summary=r["summary"] or "",
            reference_path=r["reference_path"],
            external_url=r["external_url"],
            tags=tags,
            metadata=meta,
            created_at=str(r["created_at"])
        )

    # ================= Missed Questions & Stumble Log =================

    def add_missed_question(
        self,
        title: str,
        category: str,
        what_tripped_me: str,
        company: Optional[str] = None,
        source: str = "manual_entry",
        difficulty: str = "Medium"
    ) -> MissedQuestionItem:
        now = datetime.now()
        # Spaced repetition: initial stumble scheduled for tomorrow (+1 day)
        due_date = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO missed_questions (
                title, category, company, what_tripped_me, source, difficulty,
                mastery_level, review_count, next_review_due, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
            """, (title, category, company, what_tripped_me, source, difficulty, due_date, now_str, now_str))
            conn.commit()
            new_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM missed_questions WHERE id = ?", (new_id,)).fetchone()
            return self._row_to_missed_question(row)

    def update_missed_question(
        self,
        question_id: int,
        mastery_level: Optional[int] = None,
        what_tripped_me: Optional[str] = None,
        advance_review: bool = False
    ) -> Optional[MissedQuestionItem]:
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            existing = conn.execute("SELECT * FROM missed_questions WHERE id = ?", (question_id,)).fetchone()
            if not existing:
                return None

            curr_mastery = existing["mastery_level"] if mastery_level is None else mastery_level
            curr_reviews = existing["review_count"] + (1 if advance_review else 0)
            
            # SM-2 / Leitner Spaced-Repetition Interval Calculation
            # Mastery 0 (Stumbled): +1 day
            # Mastery 1 (Reviewed / Improving): +3 days
            # Mastery 2 (Mastered): +10 days
            days_interval = 1
            if curr_mastery == 1:
                days_interval = 3
            elif curr_mastery >= 2:
                days_interval = 10
            
            next_due = (now + timedelta(days=days_interval)).strftime("%Y-%m-%d %H:%M:%S")
            tripped_text = what_tripped_me if what_tripped_me is not None else existing["what_tripped_me"]

            conn.execute("""
            UPDATE missed_questions
            SET mastery_level = ?, review_count = ?, what_tripped_me = ?, next_review_due = ?, updated_at = ?
            WHERE id = ?
            """, (curr_mastery, curr_reviews, tripped_text, next_due, now_str, question_id))
            conn.commit()

            updated_row = conn.execute("SELECT * FROM missed_questions WHERE id = ?", (question_id,)).fetchone()
            return self._row_to_missed_question(updated_row)

    def list_missed_questions(
        self,
        due_only: bool = False,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[MissedQuestionItem]:
        query = "SELECT * FROM missed_questions WHERE 1=1"
        params: List[Any] = []

        if due_only:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query += " AND (next_review_due <= ? OR next_review_due IS NULL) AND mastery_level < 2"
            params.append(now_str)

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY mastery_level ASC, next_review_due ASC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_missed_question(r) for r in rows]

    def delete_missed_question(self, question_id: int) -> bool:
        with self._get_connection() as conn:
            res = conn.execute("DELETE FROM missed_questions WHERE id = ?", (question_id,))
            conn.commit()
            return res.rowcount > 0

    def _row_to_missed_question(self, r: sqlite3.Row) -> MissedQuestionItem:
        return MissedQuestionItem(
            id=r["id"],
            title=r["title"],
            category=r["category"],
            company=r["company"],
            what_tripped_me=r["what_tripped_me"],
            source=r["source"],
            difficulty=r["difficulty"],
            mastery_level=r["mastery_level"],
            review_count=r["review_count"],
            next_review_due=str(r["next_review_due"]) if r["next_review_due"] else None,
            created_at=str(r["created_at"]),
            updated_at=str(r["updated_at"])
        )

    # ================= Telemetry Methods =================

    def log_telemetry(
        self,
        topic_slug: str,
        game_type: str,
        result: str,
        card_id: Optional[str] = None,
        feedback_notes: Optional[str] = None
    ) -> LearningTelemetryItem:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO learning_telemetry (topic_slug, card_id, game_type, result, feedback_notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (topic_slug, card_id, game_type, result, feedback_notes, now_str))
            conn.commit()
            row = conn.execute("SELECT * FROM learning_telemetry WHERE id = ?", (cursor.lastrowid,)).fetchone()
            
            # If candidate stumbled on the same card or topic >= 2 times, auto-surface in missed_questions
            if result in ("stumbled", "hint_used"):
                stumble_count = conn.execute(
                    "SELECT COUNT(*) as c FROM learning_telemetry WHERE topic_slug = ? AND result IN ('stumbled', 'hint_used')",
                    (topic_slug,)
                ).fetchone()["c"]
                if stumble_count >= 2:
                    # Check if already in missed questions
                    clean_title = topic_slug.replace("_", " ").title()
                    exists = conn.execute(
                        "SELECT 1 FROM missed_questions WHERE title = ?",
                        (clean_title,)
                    ).fetchone()
                    if not exists:
                        self.add_missed_question(
                            title=clean_title,
                            category="Core CS",
                            what_tripped_me=f"Stumbled or needed hints {stumble_count} times during flashcard drill.",
                            source="flashcard_game",
                            difficulty="Medium"
                        )

            return LearningTelemetryItem(
                id=row["id"],
                topic_slug=row["topic_slug"],
                card_id=row["card_id"],
                game_type=row["game_type"],
                result=row["result"],
                feedback_notes=row["feedback_notes"],
                created_at=str(row["created_at"])
            )

    def get_telemetry_summary(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT result, COUNT(*) as count FROM learning_telemetry GROUP BY result"
            ).fetchall()
            return {r["result"]: r["count"] for r in rows}

    # ================= Stock Watchlist Methods =================

    def upsert_stock_watchlist(
        self,
        ticker: str,
        company_name: str,
        current_price: Optional[float] = None,
        dcf_target_price: Optional[float] = None,
        dcf_upside_percent: Optional[float] = None,
        conviction: str = "Neutral",
        critic_warning: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> StockWatchlistItem:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute("""
            INSERT INTO stock_watchlist (
                ticker, company_name, current_price, dcf_target_price, dcf_upside_percent,
                conviction, critic_warning, run_id, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
                company_name=excluded.company_name,
                current_price=COALESCE(excluded.current_price, stock_watchlist.current_price),
                dcf_target_price=COALESCE(excluded.dcf_target_price, stock_watchlist.dcf_target_price),
                dcf_upside_percent=COALESCE(excluded.dcf_upside_percent, stock_watchlist.dcf_upside_percent),
                conviction=excluded.conviction,
                critic_warning=COALESCE(excluded.critic_warning, stock_watchlist.critic_warning),
                run_id=COALESCE(excluded.run_id, stock_watchlist.run_id),
                updated_at=excluded.updated_at;
            """, (
                ticker.upper(), company_name, current_price, dcf_target_price,
                dcf_upside_percent, conviction, critic_warning, run_id, now_str
            ))
            conn.commit()
            row = conn.execute("SELECT * FROM stock_watchlist WHERE ticker = ?", (ticker.upper(),)).fetchone()
            return self._row_to_stock_item(row)

    def list_stock_watchlist(self) -> List[StockWatchlistItem]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM stock_watchlist ORDER BY updated_at DESC").fetchall()
            return [self._row_to_stock_item(r) for r in rows]

    def _row_to_stock_item(self, r: sqlite3.Row) -> StockWatchlistItem:
        return StockWatchlistItem(
            ticker=r["ticker"],
            company_name=r["company_name"],
            current_price=r["current_price"],
            dcf_target_price=r["dcf_target_price"],
            dcf_upside_percent=r["dcf_upside_percent"],
            conviction=r["conviction"] or "Neutral",
            critic_warning=r["critic_warning"],
            run_id=r["run_id"],
            last_updated=str(r["updated_at"])
        )
