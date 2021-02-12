import sqlite3
import pandas as pd
import PYTHON.data_cleaning_functions as dcf


def current_season_cleaner():

    path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/'

    db_connection = sqlite3.connect(path + 'seasons.sqlite')

    gameweeks_df = pd.read_csv(path + 'CSV/raw_gameweek_data/gameweeks-2020-21.csv')
    odds_df = pd.read_csv(path + 'CSV/bookies_odds/odds-2020-21.csv')

    gameweeks_df = dcf.minutes_played(gameweeks_df)

    dcf.add_season('2020-21', gameweeks_df)

    gameweeks_df["plays_for"] = gameweeks_df["team"].replace({"Sheffield Utd": "Sheffield United", "Spurs": "Tottenham",
                                                              "Man Utd": "Man United"})
    
    dcf.adjust_points(gameweeks_df)

    dcf.clean_team_names(gameweeks_df, odds_df)

    gameweeks_df['opponent_team'] = gameweeks_df['opponent_team'].replace({'Leicester': 'Leeds', 'Leeds': 'Leicester'})

    dcf.dates_cleaner(gameweeks_df)

    dcf.home_and_away_teams(gameweeks_df)

    gameweeks_df = dcf.odds_joiner(gameweeks_df, odds_df, '202021', db_connection)

    dcf.win_expectation(gameweeks_df, 'normal')

    dcf.won_the_game(gameweeks_df)

    dcf.mean_statistics(gameweeks_df)

    dcf.shift_match_info(gameweeks_df)

    dcf.useful_columns(gameweeks_df).to_csv(path + 'CSV/clean_season_data/clean-2020-21.csv', index=False)
