# 두산 베어스 알림

두산 베어스 **주말 홈경기 예매가 임박하면** FCM 푸시로 알려주는 앱.

> 예매 오픈 시각 데이터는 두산 사이트 로그인 안에 있어 직접 감시가 불가능합니다.
> 그래서 공개 일정에서 **주말(토·일) 홈경기**를 골라, 경기 며칠 전에
> "예매 오픈 예정 / 예매 임박" 리마인더를 보냅니다 (`backend/reminder.py`).
> 단계는 `config.py`의 `REMIND_STAGES`에서 조정합니다 (기본: 7일 전, 2일 전).
>
> (참고: '새 경기 일정 등록' 알림 코드도 `poller.py`에 남아 있습니다.)

```
backend/  : 네이버 KBO 일정을 폴링 → 새 gameId 감지 → FCM 토픽으로 푸시
app/      : Flutter 앱 (FCM 'doosan_games' 토픽 구독 + 일정 표시)
```

## 동작 원리

1. 백엔드가 10분마다 네이버 스포츠 KBO 일정 API에서 두산(`OB`) 경기를 가져온다.
2. SQLite에 저장된 기존 `gameId` 목록과 비교해 **새 경기**를 찾는다.
3. 새 경기가 있으면 FCM 토픽 `doosan_games`로 푸시를 발송한다.
4. 앱은 이 토픽을 구독하고 있어 알림을 받는다.

> 최초 실행 시에는 기존 일정 전체를 '알림 없이' 저장(시드)만 합니다.
> 이후 새로 추가되는 경기에 대해서만 푸시가 갑니다.

## 빠른 시작

### 1. Firebase 프로젝트 준비 (공통)
1. https://console.firebase.google.com 에서 프로젝트 생성
2. Android 앱 등록 → `google-services.json` 다운로드 → `app/android/app/`에 배치
   (iOS는 `GoogleService-Info.plist`)
3. 프로젝트 설정 → 서비스 계정 → **새 비공개 키 생성** →
   받은 JSON을 `backend/serviceAccountKey.json`으로 저장

### 2. 백엔드 실행
```bash
cd backend
pip install -r requirements.txt
python poller.py            # 폴링 시작 (최초엔 시드만, 이후 새 경기 푸시)
```
환경변수로 조정 가능: `POLL_INTERVAL_SEC`, `LOOKAHEAD_DAYS`, `FCM_TOPIC` 등 (config.py 참고)

### 3. 앱 실행
```bash
cd app
flutter create .                    # 플랫폼 폴더(android/ios) 생성
dart pub global activate flutterfire_cli
flutterfire configure               # firebase_options.dart 자동 생성
flutter pub get
flutter run
```

## GitHub Actions로 무료 가동 (서버 불필요)

PC를 켜둘 필요 없이 GitHub가 주기적으로 폴링·푸시합니다.

1. 이 프로젝트를 GitHub 레포에 push
2. 레포 **Settings → Secrets and variables → Actions → New repository secret**
   - 이름: `FIREBASE_CREDENTIALS`
   - 값: `serviceAccountKey.json` 파일 **내용 전체**(JSON)를 붙여넣기
3. **Settings → Actions → General → Workflow permissions** → "Read and write permissions" 체크
   (`games.db` 상태 커밋을 위해 필요)
4. 끝. `.github/workflows/poll.yml`이 30분마다 자동 실행됩니다.
   - **Actions** 탭에서 "Run workflow"로 수동 테스트도 가능

동작 방식:
- 매 실행마다 `run_once.py`가 1회 폴링 → 새 경기 있으면 FCM 푸시
- "이미 본 경기" 상태(`games.db`)를 레포에 다시 커밋해 다음 실행 때 비교
- 첫 실행은 기존 일정을 알림 없이 시드만 함 (이후부터 새 경기 알림)

> ⚠️ Actions cron은 보통 5~30분 지연됩니다. 일정 등록 알림에는 충분하지만,
> 분 단위 정확도가 필요하면 Railway/Fly.io 같은 상시 가동 호스팅을 쓰세요.

## 다음 단계 (로드맵)
- [ ] 상시 가동이 필요하면 Railway / Fly.io 로 이전
- [ ] '경기 시작 임박' 알림 추가 (gameDateTime 기준 스케줄링)
- [ ] '실시간 스코어/결과' 알림 추가 (statusCode 변동 감지)
- [ ] 앱 내 알림 on/off 설정 화면

## 주의
- 네이버 API는 비공식이라 응답 형식이 바뀔 수 있습니다. 변경 시 `naver.py`의 파싱부만 수정하면 됩니다.
- 폴링 주기를 너무 짧게(예: 10초) 두지 마세요. 차단 위험과 불필요한 부하가 있습니다.
