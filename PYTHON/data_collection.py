import urllib.request


def get_data():

    path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/CSV/'

    # Downloads the latest merged CSV file from the Github recourse for the players 2020-21 FPL data.
    fpl_data_url = 'https://github.com/vaastav/Fantasy-Premier-League/raw/master/data/2020-21/gws/merged_gw.csv'
    urllib.request.urlretrieve(fpl_data_url, path + 'raw_gameweek_data/gameweeks-2020-21.csv')

    # Downloads the latest CSV file with the bookies odds for the 2020-21 season.
    bookies_odds_url = 'https://www.football-data.co.uk/mmz4281/2021/E0.csv'
    urllib.request.urlretrieve(bookies_odds_url, path + 'bookies_odds/odds-2020-21.csv')
