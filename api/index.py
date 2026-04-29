from http.server import BaseHTTPRequestHandler
from urllib import parse
import json
import requests
import os

# Vercel 환경 변수에서 API 키를 안전하게 불러옵니다.
PUBG_API_KEY = os.environ.get("PUBG_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {PUBG_API_KEY}",
    "Accept": "application/vnd.api+json"
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
        player_name = query.get("player")
        last_match_id = query.get("lastMatch")

        self.send_response(200)
        # CORS 설정: GitHub Pages에서 접근할 수 있도록 허용
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if not player_name:
            self.wfile.write(json.dumps({"error": "Player name required"}).encode('utf-8'))
            return

        try:
            # 1. 유저 Account ID 조회 (Steam 플랫폼 기준)
            url_player = f"https://api.pubg.com/shards/steam/players?filter[playerNames]={player_name}"
            res_player = requests.get(url_player, headers=HEADERS).json()
            account_id = res_player['data'][0]['id']

            # 2. 최근 매치 ID 1개 가져오기
            url_account = f"https://api.pubg.com/shards/steam/players/{account_id}"
            res_account = requests.get(url_account, headers=HEADERS).json()
            latest_match_id = res_account['data']['relationships']['matches']['data'][0]['id']

            # 3. 새로운 매치가 없다면 종료
            if latest_match_id == last_match_id:
                self.wfile.write(json.dumps({"status": "no_new_match", "matchId": latest_match_id}).encode('utf-8'))
                return

            # 4. 새로운 매치라면 상세 데이터 조회
            url_match = f"https://api.pubg.com/shards/steam/matches/{latest_match_id}"
            res_match = requests.get(url_match, headers=HEADERS).json()

            player_stats = {}
            # included 배열에서 참여자(participant) 데이터만 파싱
            for item in res_match.get('included', []):
                if item['type'] == 'participant':
                    stats = item['attributes']['stats']
                    name = stats['name']
                    kills = stats['kills']
                    # 배틀그라운드 API는 death 카운트가 명시적으로 없으므로, 살아남지 못했다면 1데스로 처리
                    deaths = 1 if stats['deathType'] != 'alive' else 0
                    
                    player_stats[name] = {"kills": kills, "deaths": deaths}

            result = {
                "status": "new_match",
                "matchId": latest_match_id,
                "stats": player_stats
            }
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))