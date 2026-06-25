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
