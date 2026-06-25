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


def send_ticket_reminder(game: dict, stage_label: str) -> str:
    """주말 홈경기 예매 오픈 단계별 알림을 토픽 구독자에게 푸시한다."""
    _ensure_init()

    open_dt = game.get("open_dt")
    # 윈도우 strftime은 %-m 미지원이라 수동 포맷
    open_str = (
        f"{open_dt.month}/{open_dt.day} {open_dt.hour:02d}:{open_dt.minute:02d}"
        if open_dt else ""
    )

    match_line = (
        f"{game['weekday']} {game['game_date']} "
        f"{config.TEAM_NAME} vs {game['away_name']} ({game['stadium']})"
    )

    if stage_label == "지금 예매 오픈":
        title = "🎟️ 지금 예매 오픈!"
        body = f"{match_line}\n지금 바로 예매하세요 → 두산 홈페이지/인터파크"
    elif stage_label == "예매 오픈 임박":
        title = "⏰ 예매 오픈 임박"
        body = f"{match_line}\n{open_str} 예매 오픈! 미리 로그인해 대기하세요."
    else:  # 예매 오픈 예정
        title = "🎟️ 예매 오픈 예정"
        body = f"{match_line}\n{open_str} 예매 오픈 예정입니다."

    message = messaging.Message(
        topic=config.FCM_TOPIC,
        notification=messaging.Notification(title=title, body=body),
        data={
            "type": "ticket_reminder",
            "stage": stage_label,
            "game_id": str(game["game_id"]),
            "game_date": str(game["game_date"]),
            "ticket_url": config.TICKET_URL,
        },
        android=messaging.AndroidConfig(priority="high"),
    )
    return messaging.send(message)
