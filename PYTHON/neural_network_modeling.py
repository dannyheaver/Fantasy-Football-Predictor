from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV
from modeling_preperation import x_train, y_train
import pickle

model = MLPClassifier()

parameters = {
    'solver': ['sgd'],
    'hidden_layer_sizes': [(600, 600, )]
}

gridsearch = GridSearchCV(model, parameters, cv=5)

gridsearch.fit(x_train, y_train)

print(gridsearch.best_estimator_)
print(gridsearch.best_score_)

path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/'

pickle.dump(gridsearch.best_estimator_, open(path + 'best_model.sav', 'wb'))
