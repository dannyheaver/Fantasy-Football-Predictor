from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
import numpy as np
from datetime import datetime
from sklearn.metrics import precision_score, recall_score, f1_score


def split_and_scale(predictors, labels, scaler, numerical_columns, test_size=0.2, stratify=None, random_state=1):
    """
    Performs a train-test split and then transforms the numerical columns in both the training and test sets using a
     feature scaler that is fitted to the training set. The feature names are therefore the same as the
     dummified predictors columns.

    :param predictors: The dummified predictors.
    :param labels: Corresponding labels.
    :param scaler: The feature scaler to transform the numerical columns in the predictors.
    :param numerical_columns: The columns to feature scale.
    :param test_size: The size of the test size in the train-test split.
    :param stratify: How to stratify the train-test split. Default is None.
    :param random_state: The random state of the train-test split.
    :return: (training_predictors_as_sparse_matrix, test_predictors_as_sparse_matrix, training_labels, test_labels, transformer)
    """
    x_train, x_test, y_train, y_test = train_test_split(predictors, labels, test_size=test_size, stratify=stratify,
                                                        random_state=random_state)
    transformer = ColumnTransformer([('numerical', scaler, numerical_columns)],
                                    remainder='passthrough')
    x_train = transformer.fit_transform(x_train)
    x_test = transformer.transform(x_test)
    return np.array(x_train), np.array(x_test), y_train, y_test, transformer


def classification_evaluation(model, x_train, x_test, y_train, y_test, cv=5):
    """
    A function which takes a classification machine learning algorithm and fits it to the training set of predictors. It
    then evaluates the model using various statistical measures.

    :param model: The machine learning algorithm to fit and evaluate
    :param x_train: The training predictors
    :param x_test: The test predictors
    :param y_train: The training labels
    :param y_test: The test labels
    :param cv: The number of folds in the cross-validation
    :return: (mean_cv_score, training_score, test_score, precision_score, recall_score, f1_score, time_taken)
    """
    start_time = datetime.now()
    cv_score = cross_val_score(model, x_train, y_train, cv=cv, n_jobs=-1).mean()
    model.fit(x_train, y_train)
    train_score = model.score(x_train, y_train)
    test_score = model.score(x_test, y_test)
    predictions = model.predict(x_test)
    precision = precision_score(y_test, predictions, average='weighted')
    recall = recall_score(y_test, predictions, average='weighted')
    f1 = f1_score(y_test, predictions, average='weighted')
    time_taken = datetime.now() - start_time
    return cv_score, train_score, test_score, precision, recall, f1, time_taken
