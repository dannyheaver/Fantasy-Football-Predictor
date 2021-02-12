import sqlite3
import pandas as pd
import glob
import PYTHON.data_cleaning_functions as dcf


def season_concatenator():

    path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/'

    db_connection = sqlite3.connect(path + 'seasons.sqlite')

    gameweeks_df = pd.concat(map(pd.read_csv, glob.glob(path + "CSV/clean_season_data/*.csv")))

    gameweeks_df = dcf.attacking_or_defending(gameweeks_df, db_connection)

    dcf.form_against_next_opponent(gameweeks_df, gameweeks_df)

    dcf.shifted_points_range(gameweeks_df)

    gameweeks_df.to_csv(path + 'CSV/all_gameweeks.csv', index=False)
