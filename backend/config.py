"""설정값 모음. 환경변수로 덮어쓸 수 있습니다."""
import os

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

# 리마인더 단계: (경기 며칠 전, 라벨). 가까워질수록 한 번씩 알림.
#  - 7일 전: "예매 오픈 예정" (나)
#  - 2일 전: "예매 임박" (가)
REMIND_STAGES = [
    (int(os.getenv("REMIND_DAYS_NOTICE", "7")), "예매 오픈 예정"),
    (int(os.getenv("REMIND_DAYS_SOON", "2")), "예매 임박"),
]

# 주말만 알림 (월=0 ... 토=5, 일=6)
WEEKEND_WEEKDAYS = {5, 6}
