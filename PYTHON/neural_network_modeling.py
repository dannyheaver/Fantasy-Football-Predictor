from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV
from PYTHON.modeling_preperation import x_train, y_train
import pickle


def train_model():

    model = MLPClassifier(solver='sgd', hidden_layer_sizes=(600, 600, ), max_iter=1000)

    model.fit(x_train, y_train)

    pickle.dump(gridsearch.best_estimator_, open('/Users/danielheaver/Desktop/projects/fantasy_football_predictions/best_model.sav', 'wb'))
