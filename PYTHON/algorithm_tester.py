from tqdm import tqdm
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB, ComplementNB, BernoulliNB, CategoricalNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from modeling_preperation import x_train, x_test, y_train, y_test
import modeling_functions as mf

path = '/Users/danielheaver/Desktop/projects/fantasy_football_predictions/CSV/'

models = [
    LogisticRegression(solver='liblinear', penalty='l1', class_weight='balanced', max_iter=5000),
    LogisticRegression(class_weight='balanced', max_iter=5000, n_jobs=-1),
    LogisticRegression(l1_ratio=0.9, solver='saga', penalty='elasticnet', class_weight='balanced', max_iter=6000, n_jobs=-1),
    KNeighborsClassifier(),
    GaussianNB(),
    MultinomialNB(),
    ComplementNB(),
    BernoulliNB(),
    DecisionTreeClassifier(class_weight='balanced'),
    RandomForestClassifier(class_weight='balanced', n_jobs=-1),
    SVC(class_weight='balanced', kernel='linear'),
    SVC(class_weight='balanced', kernel='poly'),
    SVC(class_weight='balanced'),
    MLPClassifier(solver='lbfgs'),
    MLPClassifier(solver='sgd', max_iter=5000),
    MLPClassifier(solver='adam')
]

scores = []
for model in tqdm(models):
    try:
        scores.append(mf.classification_evaluation(model, x_train, x_test, y_train, y_test))
    except:
        scores.append(None)

model_scores = pd.DataFrame(scores, columns=['Mean CV Score', 'Train Score', 'Test Score', 'Precision Score',
                                             'Recall Score', 'f1 Score', 'Time Taken (s)'])
model_scores.insert(0, 'Model', models)

model_scores.to_csv(path + 'model_scores.csv', index=False)
