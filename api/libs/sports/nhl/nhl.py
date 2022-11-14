import json, pickle, redis

from jockbot_nhl import NHL, NHLTeam

API = Flask(__name__)
REDIS = redis.Redis(host='172.17.0.3', port=6379, db=0)

def _nhl_wildcard_check(team):
    wildcard_status = False
    wildcard = NHL().wildcard_standings
    east = wildcard['Eastern']
    west = wildcard['Western']
    if team in east:
        for k, v in east.items():
            if team == k and v == '1':
                wildcard_status = True
                break
            elif team == k and v == '2':
                wildcard_status = True
                break
    if team in west:
        for k, v in west.items():
            if team == k and v == '1':
                wildcard_status = True
                break
            elif team == k and v == '2':
                wildcard_status = True
                break
    return wildcard_status

@API.route('/v1/hockey/<team>')
def hockey_team_info(team):
    all_stars = ['Atlantic', 'Metropolitan', 'Central', 'Pacific']
    key = f'/v1/hockey/{team}'
    if team in all_stars or team.title() in all_stars:
        team_data = {
            'record': {
                'wins': 0,
                'losses': 0,
                'ot': 0,
                'type': 'league',
                'division_rank': '1',
                'conference_rank': '1',
                'overall_rank': '1'
            },
            'games_played': 1,
            'points': 0
        }
        return _send_response(json.dumps(team_data))
    data = REDIS.get(key)
    if not data:
        team_data = NHLTeam(team)
        data = team_data.record
        data['record']['division_rank'] = team_data.division_rank
        data['record']['conference_rank'] = team_data.conference_rank
        data['record']['overall_rank'] = team_data.overall_rank
        REDIS.set(key, pickle.dumps(data), nx=True)
    else:
        data = pickle.loads(data)
    return _send_response(json.dumps(data))


@API.route('/v1/hockey/league/games/recent-scores')
def nhl_recent_scores():
    key = '/v1/hockey/league/recent-scores'
    games = REDIS.get(key)
    if not games:
        nhl = NHL()
        games = nhl.recent_scores
        REDIS.set(key, pickle.dumps(games), ex=86400)
    else:
        games = pickle.loads(games)
    return _send_response(json.dumps(games))


@API.route('/v1/hockey/league/games')
def nhl_upcoming_games():
    key = '/v1/hockey/league/games'
    games = REDIS.get(key)
    if not games:
        nhl = NHL()
        games = nhl.todays_games
        REDIS.set(key, pickle.dumps(games), ex=300)
    else:
        games = pickle.loads(games)
    return _send_response(json.dumps(games))


@API.route('/v1/hockey/league/standings/overall')
def nhl_league_standings() -> list:
    key = '/v1/hockey/league/standings/overall'
    standings = REDIS.get(key)
    if not standings:
        standings = []
        nhl = NHL()
        league_standings = nhl.league_standings
        records = nhl.team_records
        for team, rank in league_standings.items():
            data = {}
            record = records.get(team)
            record['rank'] = rank
            data['name'] = team
            data['record'] = record
            standings.append(data)
        REDIS.set(key, pickle.dumps(standings), ex=86400)
    else:
        standings = pickle.loads(standings)
    return _send_response(json.dumps(standings))


@API.route('/v1/hockey/league/standings/conference')
def nhl_conference_standings() -> dict:
    key = '/v1/hockey/league/standings/conference'
    standings = REDIS.get(key)
    if not standings:
        standings = {}
        nhl = NHL()
        conf_standings = nhl.conference_standings
        records = nhl.team_records
        for conference, teams in conf_standings.items():
            teams = {k: v for k, v in sorted(conf_standings[conference].items(), key=lambda item: int(item[1]))}
            standings[conference] = []
            for team, rank in teams.items():
                data = {}
                record = records.get(team)
                record['rank'] = rank
                data['name'] = team
                data['record'] = record
                data['wildcard_status'] = _nhl_wildcard_check(team)
                standings[conference].append(data)
        REDIS.set(key, pickle.dumps(standings), ex=86400)
    else:
        standings = pickle.loads(standings)
    return _send_response(json.dumps(standings))


@API.route('/v1/hockey/league/standings/division')
def nhl_division_standings() -> dict:
    key = '/v1/hockey/league/standings/division'
    standings = REDIS.get(key)
    if not standings:
        standings = {}
        nhl = NHL()
        division_standings = nhl.division_standings
        records = nhl.team_records
        for division, teams in division_standings.items():
            # teams = {k: v for k, v in sorted(conference_standings[conference].items(), key=lambda item: int(item[1]))}
            standings[division] = []
            for team, rank in teams.items():
                data = {}
                record = records.get(team)
                record['rank'] = rank
                data['name'] = team
                data['record'] = record
                data['wildcard_status'] = _nhl_wildcard_check(team)
                standings[division].append(data)
        REDIS.set(key, pickle.dumps(standings), ex=86400)
    else:
        standings = pickle.loads(standings)
    return _send_response(json.dumps(standings))


@API.route('/v1/hockey/<team>/schedule')
def nhl_team_schedule(team):
    key = f'/v1/hockey/{team}/schedule'
    data = REDIS.get(key)
    if not data:
        team = NHLTeam(team)
        data = team.get_all_games()
        REDIS.set(key, pickle.dumps(data))
    else:
        data = pickle.loads(data)
    return _send_response(json.dumps(data))