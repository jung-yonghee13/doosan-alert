"""네이버 스포츠 KBO 일정 API 클라이언트."""
from datetime import date, timedelta

import requests

import config

API_URL = "https://api-gw.sports.naver.com/schedule/games"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.sports.naver.com/"}


def fetch_team_games(team_code: str, lookahead_days: int) -> list[dict]:
    """오늘부터 lookahead_days 후까지의 해당 팀 경기 목록을 반환한다."""
    today = date.today()
    params = {
        "fields": "basic,schedule",
        "upperCategoryId": "kbaseball",
        "categoryId": "kbo",
        "fromDate": today.isoformat(),
        "toDate": (today + timedelta(days=lookahead_days)).isoformat(),
        "size": 500,
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    games = data.get("result", {}).get("games", [])
    team_games = [
        g
        for g in games
        if g.get("homeTeamCode") == team_code or g.get("awayTeamCode") == team_code
    ]
    return [_normalize(g) for g in team_games]


def _normalize(g: dict) -> dict:
    """필요한 필드만 추려서 평탄화한다."""
    return {
        "game_id": g["gameId"],
        "game_date": g.get("gameDate"),
        "game_datetime": g.get("gameDateTime"),
        "stadium": g.get("stadium"),
        "home_code": g.get("homeTeamCode"),
        "home_name": g.get("homeTeamName"),
        "away_code": g.get("awayTeamCode"),
        "away_name": g.get("awayTeamName"),
        "status": g.get("statusCode"),
    }


if __name__ == "__main__":
    # 단독 실행 시 동작 확인용
    rows = fetch_team_games(config.TEAM_CODE, config.LOOKAHEAD_DAYS)
    print(f"{config.TEAM_NAME} 경기 {len(rows)}건")
    for r in rows[:5]:
        print(f"  {r['game_date']} {r['away_name']} @ {r['home_name']} ({r['stadium']})")
