def celtics_games(season=None):
    """Generator for Celtic's remaining regular season games"""
    if not season:
        season = get_current_nba_season()
    url = f"https://www.basketball-reference.com/teams/BOS/{season}_games.html"
    request = requests.get(url)
    if request.status_code == 404:
        return
    soup = BeautifulSoup(request.content, 'html.parser')
    schedule = soup.find('table')
    schedule_rows = schedule.find_all('tr')
    for row in schedule_rows:
        game_data = {}
        data_cells = row.find_all('td')
        for cell in data_cells:
            data = cell.attrs.get('data-stat')
            if data:
                game_data[data] = cell.text
        if game_data:
            yield parse_game(game_data)