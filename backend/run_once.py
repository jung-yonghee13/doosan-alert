"""GitHub Actions 등에서 1회만 폴링하고 종료한다 (cron 트리거용)."""
import logging

import store
from poller import check_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    store.init_db()
    sent = check_once()
    logging.getLogger("run_once").info("완료: %d건 푸시", sent)
