"""Firebase Cloud Messaging 토픽 푸시 발송."""
import firebase_admin
from firebase_admin import credentials, messaging

import config

_initialized = False


def _ensure_init() -> None:
    global _initialized
    if not _initialized:
        cred = credentials.Certificate(config.FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred)
        _initialized = True


def send_new_game(game: dict) -> str:
    """새 경기 1건을 토픽 구독자에게 푸시한다. 반환값은 메시지 ID."""
    _ensure_init()

    date_str = game.get("game_date", "")
    title = f"⚾ {config.TEAM_NAME} 새 경기 일정"
    body = f"{date_str} {game['away_name']} vs {game['home_name']} ({game['stadium']})"

    message = messaging.Message(
        topic=config.FCM_TOPIC,
        notification=messaging.Notification(title=title, body=body),
        data={
            "type": "new_game",
            "game_id": str(game["game_id"]),
            "game_date": str(date_str),
        },
        android=messaging.AndroidConfig(priority="high"),
    )
    return messaging.send(message)
