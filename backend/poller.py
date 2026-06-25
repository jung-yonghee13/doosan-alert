"""메인 폴링 루프: 새 경기 일정 감지 → FCM 푸시."""
import logging
import time

import config
import fcm
import naver
import store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("poller")


def check_once() -> int:
    """1회 폴링. 새로 발견·알림한 경기 수를 반환."""
    games = naver.fetch_team_games(config.TEAM_CODE, config.LOOKAHEAD_DAYS)
    seen = store.known_ids()
    new_games = [g for g in games if g["game_id"] not in seen]

    if not new_games:
        log.info("새 경기 없음 (총 %d건 확인)", len(games))
        return 0

    # 첫 실행이면 기존 일정 전체를 '알림 없이' 시드만 한다.
    if not store.is_seeded():
        store.save_games(games)
        store.mark_seeded()
        log.info("최초 시드 완료: %d건 저장 (알림 미발송)", len(games))
        return 0

    sent = 0
    for g in new_games:
        try:
            msg_id = fcm.send_new_game(g)
            log.info(
                "푸시 발송: %s %s vs %s (msg=%s)",
                g["game_date"], g["away_name"], g["home_name"], msg_id,
            )
            sent += 1
        except Exception:
            log.exception("푸시 발송 실패: %s", g["game_id"])

    # 발송 성공 여부와 무관하게 저장(다음 루프에서 재발송 방지). 실패 재시도가 필요하면 여기 조정.
    store.save_games(new_games)
    return sent


def main() -> None:
    store.init_db()
    log.info(
        "폴링 시작: 팀=%s, 토픽=%s, 주기=%ds",
        config.TEAM_NAME, config.FCM_TOPIC, config.POLL_INTERVAL_SEC,
    )
    while True:
        try:
            check_once()
        except Exception:
            log.exception("폴링 루프 오류")
        time.sleep(config.POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()
