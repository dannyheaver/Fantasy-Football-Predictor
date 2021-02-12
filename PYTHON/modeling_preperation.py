import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import PYTHON.modeling_functions as mf

path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/CSV/'

gameweeks = pd.read_csv(path + 'all_gameweeks.csv')

gameweeks.drop(['round', 'date_of_match'], axis=1, inplace=True)

predictors = gameweeks[gameweeks['shift_points_range'].notna()]
labels = predictors.pop('shift_points_range')

categorical = ['season', 'name', 'position', 'plays_for', 'opponent_team', 'was_home', 'won', 'month_of_match',
               'time_of_match', 'shift_opponent', 'shift_month_of_match', 'shift_time_of_match', 'shift_was_home']

predictors_dummified = pd.get_dummies(predictors, columns=categorical)

numerical = [col for col in predictors.columns if col not in categorical]

x_train, x_test, y_train, y_test, transformer = mf.split_and_scale(predictors_dummified, labels, MinMaxScaler(),
                                                                   numerical, stratify=labels)
