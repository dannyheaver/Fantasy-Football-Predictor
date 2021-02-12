import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time as t
from bs4 import BeautifulSoup
import numpy as np
import PYTHON.data_cleaning_functions as dcf


def get_next_fixtures():

    path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/'

    db_connection = sqlite3.connect(path + 'seasons.sqlite')

    gameweeks = pd.read_csv(path + 'CSV/all_gameweeks.csv')

    next_fixtures = gameweeks[(gameweeks['season'] == '2020-21') & (gameweeks['shift_points_range'].isnull()) &
                              (gameweeks['round'] >= max(gameweeks[gameweeks['season'] == '2020-21']['round']) - 5)].copy()

    next_round = max(next_fixtures['round']) + 1

    next_fixtures.dropna(axis=1, inplace=True)

    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(executable_path='/Users/danielheaver/Desktop/chromedriver', options=chrome_options)
    driver.get('https://s5.sir.sportradar.com/bet365/en/1/season/77179/fixtures/round/21-{}'.format(next_round))
    t.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    table = soup.find('tbody', attrs={'class': ''})
    table_rows = table.find_all('tr')

    all_info = []
    for row in table_rows[1:]:
        if 'table-subheader no-wrap text-left' in str(row):
            date = row.text.replace('1X21X2HTFT', '')
        elif 'row flex-items-xs-middle flex-items-xs-around' in str(row):
            time = row.find('td', attrs={'class': 'mobile-width-5 text-center'}).text
            teams = row.find_all('div', attrs={'class': 'col-xs-5'})
            home_team = teams[0].text[:-3]
            away_team = teams[1].text[:-3]
            odds = row.find_all('div', attrs={'class': 'col-xs-4'})
            try:
                home_odds = float(odds[0].text)
                away_odds = float(odds[2].text)
            except IndexError:
                home_odds = np.nan
                away_odds = np.nan
            # noinspection PyUnboundLocalVariable
            all_info.append((date, time, home_team, home_odds, away_team, away_odds))

    next_odds = pd.DataFrame(all_info, columns=['shift_date_of_match', 'shift_time_of_match', 'shift_home_team', 'B365H',
                                                'shift_away_team', 'B365A'])

    next_odds['shift_month_of_match'] = pd.to_datetime(next_odds['shift_date_of_match']).dt.month

    next_odds[['shift_home_team', 'shift_away_team']] = next_odds[['shift_home_team', 'shift_away_team']].replace({'Wolverhampton': 'Wolves', 'West Bromwich': 'West Brom', 'Sheffield': 'Sheffield United', 'Man Utd': 'Man United', 'Leed': 'Leeds'})

    next_fixtures = dcf.next_odds_joiner(next_fixtures, next_odds, db_connection)

    dcf.shifted_was_home(next_fixtures)

    dcf.shifted_opponent(next_fixtures)

    dcf.win_expectation(next_fixtures, 'shift')

    dcf.shift_match_stats_for_next_fixtures(next_fixtures, gameweeks)

    next_fixtures = dcf.useful_columns(next_fixtures)

    dcf.form_against_next_opponent(next_fixtures, gameweeks)

    dcf.fill_null_shift_opponent(next_fixtures)

    next_fixtures.to_csv(path + 'CSV/predictions/next_fixtures.csv', index=False)
