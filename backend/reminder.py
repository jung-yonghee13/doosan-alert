"""주말 홈경기 예매 오픈 알림 (옵션 B).

예매 오픈 시각 데이터는 로그인 안에 잠겨 있어 직접 감시가 불가능하므로,
공개된 예매 규칙(경기일 N일 전 오전 H시 오픈)으로 오픈 시각을 계산해
'주말(토·일) 홈경기'에 대해 단계별 알림을 보낸다.

단계(오픈 시각 기준):
  - "예매 오픈 예정"  : 오픈 24시간 전 ~ 임박 직전
  - "예매 오픈 임박"  : 오픈 90분 전 ~ 오픈 시각
  - "지금 예매 오픈"  : 오픈 시각 ~ 이후 몇 시간 내
각 단계는 (game_id, 단계)별로 1회만 발송한다.
"""
import logging
from datetime import datetime, timedelta

import config
import fcm
import naver
import store

log = logging.getLogger("reminder")

_WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def _weekend_home_games(games: list[dict]) -> list[dict]:
    """주말(토·일) + 홈경기만 추려, 요일/예매오픈시각을 덧붙여 반환."""
    result = []
    for g in games:
        if g.get("home_code") != config.TEAM_CODE:
            continue  # 홈경기만
        try:
            d = datetime.strptime(g["game_date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        if d.weekday() not in config.WEEKEND_WEEKDAYS:
            continue  # 주말만
        # 예매 오픈 시각 = 경기일 - N일, 오전 H시 (KST)
        open_dt = (d - timedelta(days=config.TICKET_OPEN_DAYS_BEFORE)).replace(
            hour=config.TICKET_OPEN_HOUR, minute=0, second=0, microsecond=0,
            tzinfo=config.KST,
        )
        g = dict(g)
        g["weekday"] = f"({_WEEKDAY_KR[d.weekday()]})"
        g["open_dt"] = open_dt
        result.append(g)
    return result


def _stage_for(open_dt: datetime, now: datetime) -> str | None:
    """현재 시각이 어느 알림 단계에 해당하는지 결정. 없으면 None."""
    notice_start = open_dt - timedelta(hours=config.NOTICE_LEAD_HOURS)
    imminent_start = open_dt - timedelta(minutes=config.IMMINENT_LEAD_MIN)
    open_end = open_dt + timedelta(hours=config.OPEN_GRACE_HOURS)

    if open_dt <= now < open_end:
        return "지금 예매 오픈"
    if imminent_start <= now < open_dt:
        return "예매 오픈 임박"
    if notice_start <= now < imminent_start:
        return "예매 오픈 예정"
    return None


def check_reminders(now: datetime | None = None) -> int:
    """1회 점검. 발송한 알림 수를 반환."""
    now = now or datetime.now(config.KST)
    games = naver.fetch_team_games(config.TEAM_CODE, config.LOOKAHEAD_DAYS)
    targets = _weekend_home_games(games)

    sent = 0
    for g in targets:
        stage = _stage_for(g["open_dt"], now)
        if stage is None:
            continue
        if store.already_reminded(g["game_id"], stage):
            continue
        try:
            msg_id = fcm.send_ticket_reminder(g, stage)
            log.info(
                "알림 발송: [%s] %s %s vs %s (오픈 %s, msg=%s)",
                stage, g["game_date"], config.TEAM_NAME, g["away_name"],
                g["open_dt"].strftime("%m/%d %H:%M"), msg_id,
            )
            store.mark_reminded(g["game_id"], stage)
            sent += 1
        except Exception:
            log.exception("알림 발송 실패: %s / %s", g["game_id"], stage)

    if sent == 0:
        log.info("발송할 알림 없음 (주말 홈경기 %d건 확인)", len(targets))
    return sent


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    store.init_db()
    n = check_reminders()
    print(f"완료: {n}건 발송")
