"""GitHub Actions 등에서 1회만 점검하고 종료한다 (cron 트리거용).

현재 동작: 주말 홈경기 '예매 임박 리마인더' (옵션 B).
"""
import logging

import reminder
import store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    store.init_db()
    sent = reminder.check_reminders()
    logging.getLogger("run_once").info("완료: %d건 리마인더 발송", sent)
