import sqlite3
import pandas as pd
import data_cleaning_functions as dcf

path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/'

db_connection = sqlite3.connect(path + 'seasons.sqlite')

for season in {'2016-17', '2017-18', '2018-19', '2019-20'}:

    gameweeks_df = pd.read_csv(path + 'CSV/raw_gameweek_data/gameweeks-{}.csv'.format(season))
    positions_df = pd.read_csv(path + 'CSV/raw_full_season_data/season-{}.csv'.format(season))
    odds_df = pd.read_csv(path + 'CSV/bookies_odds/odds-{}.csv'.format(season))

    gameweeks_df = dcf.minutes_played(gameweeks_df)

    dcf.add_season(season, gameweeks_df)

    dcf.gameweeks_name_cleaner(gameweeks_df)
    dcf.positions_name_cleaner(positions_df)

    gameweeks_df = dcf.position_joiner_and_cleaner(gameweeks_df, positions_df, season.replace('-', ''), db_connection)

    dcf.clean_team_names(gameweeks_df, odds_df)
    dcf.home_and_away_teams(gameweeks_df)
    dcf.played_for(gameweeks_df)

    gameweeks_df = dcf.odds_joiner(gameweeks_df, odds_df, season.replace('-', ''), db_connection)

    dcf.dates_cleaner(gameweeks_df)

    dcf.win_expectation(gameweeks_df, 'normal')

    dcf.adjust_points(gameweeks_df)

    dcf.won_the_game(gameweeks_df)

    dcf.mean_statistics(gameweeks_df)

    dcf.shift_match_info(gameweeks_df)

    dcf.useful_columns(gameweeks_df).to_csv(path + 'CSV/clean_season_data/clean-{}.csv'.format(season), index=False)
