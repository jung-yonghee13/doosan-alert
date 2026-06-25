"""주말 홈경기 예매 임박 리마인더 (옵션 B).

예매 오픈 시각 데이터는 로그인 안에 잠겨 있어 직접 감시가 불가능하므로,
공개 일정에서 '주말(토·일) 홈경기'를 골라 경기 N일 전에 리마인더를 보낸다.
"""
import logging
from datetime import date, datetime

import config
import fcm
import naver
import store

log = logging.getLogger("reminder")

_WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def _weekend_home_games(games: list[dict]) -> list[dict]:
    """주말(토·일) + 홈경기만 추려, 요일/날짜객체를 덧붙여 반환."""
    result = []
    for g in games:
        if g.get("home_code") != config.TEAM_CODE:
            continue  # 홈경기만
        try:
            d = datetime.strptime(g["game_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if d.weekday() not in config.WEEKEND_WEEKDAYS:
            continue  # 주말만
        g = dict(g)
        g["_date"] = d
        g["weekday"] = f"({_WEEKDAY_KR[d.weekday()]})"
        result.append(g)
    return result


def check_reminders(today: date | None = None) -> int:
    """1회 점검. 발송한 리마인더 수를 반환."""
    today = today or date.today()
    games = naver.fetch_team_games(config.TEAM_CODE, config.LOOKAHEAD_DAYS)
    targets = _weekend_home_games(games)

    sent = 0
    for g in targets:
        days_until = (g["_date"] - today).days
        if days_until < 0:
            continue  # 이미 지난 경기

        for stage_days, label in config.REMIND_STAGES:
            if days_until > stage_days:
                continue  # 아직 그 단계 시점 아님
            if store.already_reminded(g["game_id"], label):
                continue  # 이미 보낸 단계
            try:
                msg_id = fcm.send_ticket_reminder(g, label)
                log.info(
                    "리마인더 발송: [%s] %s %s vs %s (D-%d, msg=%s)",
                    label, g["game_date"], config.TEAM_NAME, g["away_name"],
                    days_until, msg_id,
                )
                store.mark_reminded(g["game_id"], label)
                sent += 1
            except Exception:
                log.exception("리마인더 발송 실패: %s / %s", g["game_id"], label)

    if sent == 0:
        log.info("발송할 리마인더 없음 (주말 홈경기 %d건 확인)", len(targets))
    return sent


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    store.init_db()
    n = check_reminders()
    print(f"완료: {n}건 발송")
