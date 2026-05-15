import yaml
import sys
import os
import pickle
import numpy as np
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV
from networksecurity.exception.exception import NetworkSecurityException


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def write_yaml_file(file_path: str, content: dict, replace: bool = False):
    try:
        if replace and os.path.exists(file_path):
            os.remove(file_path)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as yaml_file:
            yaml.dump(content, yaml_file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def save_numpy_array_data(file_path: str, array: np.array):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def load_numpy_array_data(file_path: str) -> np.array:
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def save_object(file_path: str, obj: object):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def load_object(file_path: str) -> object:
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def evaluate_models(x_train, y_train, x_test, y_test, models, params):
    try:
        report = {}

        for model_name, model in models.items():
            param = params.get(model_name, {})

            print("\n" + "=" * 80)
            print(f"Training model: {model_name}")
            print(f"Hyperparameters: {param if param else 'default parameters'}")
            print("=" * 80)

            gs = GridSearchCV(
                estimator=model,
                param_grid=param,
                cv=3,
                verbose=2,
                n_jobs=-1
            )
            gs.fit(x_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(x_train, y_train)

            y_test_pred = model.predict(x_test)
            test_model_score = f1_score(y_test, y_test_pred)

            report[model_name] = test_model_score

            print(f"Best params for {model_name}: {gs.best_params_}")
            print(f"F1 score for {model_name}: {test_model_score}")

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)
