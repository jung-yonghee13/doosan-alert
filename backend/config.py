"""설정값 모음. 환경변수로 덮어쓸 수 있습니다."""
import os
from datetime import timedelta, timezone

# 한국 표준시 (GitHub Actions는 UTC로 도므로 명시적으로 KST 사용)
KST = timezone(timedelta(hours=9))

# 두산 베어스 팀 코드 (네이버 스포츠 KBO 기준)
TEAM_CODE = os.getenv("TEAM_CODE", "OB")
TEAM_NAME = os.getenv("TEAM_NAME", "두산")

# FCM 푸시를 보낼 토픽 이름 (앱에서 동일한 이름으로 구독해야 함)
FCM_TOPIC = os.getenv("FCM_TOPIC", "doosan_games")

# 폴링 주기(초). 기본 10분
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "600"))

# 일정을 며칠 앞까지 조회할지 (오늘 ~ +N일)
LOOKAHEAD_DAYS = int(os.getenv("LOOKAHEAD_DAYS", "120"))

# SQLite 파일 경로
DB_PATH = os.getenv("DB_PATH", "games.db")

# Firebase 서비스 계정 키 파일 경로
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH", "serviceAccountKey.json")

# ── 예매 임박 리마인더 설정 (옵션 B) ──
# 두산 예매 페이지(로그인 필요). 알림에 링크로 첨부.
TICKET_URL = os.getenv("TICKET_URL", "https://www.doosanbears.com/ticket/reserve")

# 두산 일반 예매 규칙: 경기일 기준 N일 전 오전 H시 오픈 (공식 홈페이지/인터파크)
TICKET_OPEN_DAYS_BEFORE = int(os.getenv("TICKET_OPEN_DAYS_BEFORE", "7"))
TICKET_OPEN_HOUR = int(os.getenv("TICKET_OPEN_HOUR", "11"))

# 알림 시점(오픈 시각 기준):
#  - 하루 전 안내(나): 오픈 24시간 전 ~ 임박 직전 사이에 1회
#  - 임박(가): 오픈 90분 전 ~ 오픈 시각 사이에 1회
#  - 오픈 시작: 오픈 시각 ~ 이후 GRACE 시간 내 1회 ("지금 예매 오픈")
NOTICE_LEAD_HOURS = int(os.getenv("NOTICE_LEAD_HOURS", "24"))
IMMINENT_LEAD_MIN = int(os.getenv("IMMINENT_LEAD_MIN", "90"))
OPEN_GRACE_HOURS = int(os.getenv("OPEN_GRACE_HOURS", "6"))

# 주말만 알림 (월=0 ... 토=5, 일=6)
WEEKEND_WEEKDAYS = {5, 6}
