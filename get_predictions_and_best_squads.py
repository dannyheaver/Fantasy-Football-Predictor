from PYTHON.data_collection import get_data
from PYTHON.current_season_cleaner import current_season_cleaner
from PYTHON.season_concatenator import season_concatenator
from PYTHON.getting_next_fixtures import get_next_fixtures
from PYTHON.predicting_next_fixtures import get_predictions
from PYTHON.best_predicted_squad import get_best_squad

get_data()

current_season_cleaner()

season_concatenator()

get_next_fixtures()

get_predictions()

for constraint in {'budget', 'team', 'all', 'none'}:
    get_best_squad(constraint)
