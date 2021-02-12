import pandas as pd
import pickle
import PYTHON.data_cleaning_functions as dcf
from PYTHON.modeling_preperation import categorical, predictors_dummified, transformer


def get_predictions():

    path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/'

    next_fixtures = pd.read_csv(path + 'CSV/predictions/next_fixtures.csv')

    next_fixtures.drop(['round', 'date_of_match'], axis=1, inplace=True)

    model = pickle.load(open(path + 'best_model.sav', 'rb'))

    X_dum = pd.get_dummies(next_fixtures, columns=categorical)

    X_fixed = dcf.fix_columns(X_dum, predictors_dummified.columns)

    X_ready = transformer.transform(X_fixed)

    predictions = next_fixtures[['name', 'value', 'position', 'plays_for', 'shift_opponent']].copy()
    predictions['predicted_point_range'] = model.predict(X_ready)
    predictions[['prob_0', 'prob_1', 'prob_2', 'prob_3']] = model.predict_proba(X_ready)

    predictions['position'].replace({'AttDEF': 'DEF', 'DefDEF': 'DEF'}, inplace=True)

    predictions.to_csv(path + 'CSV/predictions/predictions.csv', index=False)
