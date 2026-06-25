"""이미 본 경기를 SQLite에 저장해 중복 알림을 막는다."""
import sqlite3
from datetime import datetime, timezone

import config


def _conn():
    return sqlite3.connect(config.DB_PATH)


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS known_games (
                game_id       TEXT PRIMARY KEY,
                game_date     TEXT,
                game_datetime TEXT,
                stadium       TEXT,
                home_name     TEXT,
                away_name     TEXT,
                first_seen    TEXT
            )
            """
        )
        # 최초 시드 여부를 기록(첫 실행 때 기존 일정 전체를 알림으로 쏘지 않기 위함)
        c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")


def is_seeded() -> bool:
    with _conn() as c:
        row = c.execute("SELECT value FROM meta WHERE key='seeded'").fetchone()
        return row is not None


def mark_seeded() -> None:
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('seeded', '1')")


def known_ids() -> set[str]:
    with _conn() as c:
        return {r[0] for r in c.execute("SELECT game_id FROM known_games")}


def save_games(games: list[dict]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as c:
        c.executemany(
            """
            INSERT OR IGNORE INTO known_games
              (game_id, game_date, game_datetime, stadium, home_name, away_name, first_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    g["game_id"],
                    g["game_date"],
                    g["game_datetime"],
                    g["stadium"],
                    g["home_name"],
                    g["away_name"],
                    now,
                )
                for g in games
            ],
        )
