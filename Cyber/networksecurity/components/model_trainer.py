import os
import sys

from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils import (
    evaluate_models,
    load_numpy_array_data,
    load_object,
    save_object
)
from networksecurity.utils.ml_utils.metric.classification_metric import (
    get_classification_score
)
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


class ModelTrainer:
    def __init__(
        self,
        data_transformation_artifact: DataTransformationArtifact,
        model_trainer_config: ModelTrainerConfig
    ):
        try:
            self.data_transformation_artifact = data_transformation_artifact
            self.model_trainer_config = model_trainer_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(
        self,
        best_model_name,
        best_model,
        best_model_score,
        classification_train_metric,
        classification_test_metric
    ):
        try:
            import mlflow
            import mlflow.sklearn

            mlflow.set_experiment("NetworkSecurity")

            with mlflow.start_run(run_name=best_model_name):
                mlflow.set_tag("best_model", best_model_name)

                mlflow.log_param("model_name", best_model_name)
                mlflow.log_params(best_model.get_params())

                mlflow.log_metric("best_model_score", best_model_score)
                mlflow.log_metric(
                    "train_f1_score",
                    classification_train_metric.f1_score
                )
                mlflow.log_metric(
                    "train_precision_score",
                    classification_train_metric.precision_score
                )
                mlflow.log_metric(
                    "train_recall_score",
                    classification_train_metric.recall_score
                )
                mlflow.log_metric(
                    "test_f1_score",
                    classification_test_metric.f1_score
                )
                mlflow.log_metric(
                    "test_precision_score",
                    classification_test_metric.precision_score
                )
                mlflow.log_metric(
                    "test_recall_score",
                    classification_test_metric.recall_score
                )
                mlflow.log_metric(
                    "f1_train_test_gap",
                    abs(
                        classification_train_metric.f1_score
                        - classification_test_metric.f1_score
                    )
                )

                mlflow.sklearn.log_model(
                    sk_model=best_model,
                    artifact_path="model"
                )

        except ModuleNotFoundError:
            logging.warning(
                "MLflow is not installed in this environment. "
                "Skipping MLflow tracking for this run."
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(self, x_train, y_train, x_test, y_test):
        try:
            models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }

            params = {
                "Decision Tree": {
                    "criterion": ["gini", "entropy", "log_loss"],
                },
                "Random Forest": {
                    "n_estimators": [8, 16, 32, 64, 128, 256],
                },
                "Gradient Boosting": {
                    "learning_rate": [0.1, 0.01, 0.05, 0.001],
                    "subsample": [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
                    "n_estimators": [8, 16, 32, 64, 128, 256],
                },
                "Logistic Regression": {},
                "AdaBoost": {
                    "learning_rate": [0.1, 0.01, 0.001],
                    "n_estimators": [8, 16, 32, 64, 128, 256],
                },
            }

            model_report = evaluate_models(
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
                models=models,
                params=params
            )

            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]

            if best_model_score < self.model_trainer_config.expected_accuracy:
                raise Exception("No best model found")

            logging.info(f"Best model found: {best_model_name}")

            y_train_pred = best_model.predict(x_train)
            classification_train_metric = get_classification_score(
                y_true=y_train,
                y_pred=y_train_pred
            )

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(
                y_true=y_test,
                y_pred=y_test_pred
            )

            diff = abs(
                classification_train_metric.f1_score
                - classification_test_metric.f1_score
            )
            if diff > self.model_trainer_config.overfitting_underfitting_threshold:
                raise Exception(
                    "Model is not generalized. Train and test score difference: "
                    f"{diff}"
                )

            self.track_mlflow(
                best_model_name=best_model_name,
                best_model=best_model,
                best_model_score=best_model_score,
                classification_train_metric=classification_train_metric,
                classification_test_metric=classification_test_metric
            )

            preprocessor = load_object(
                file_path=(
                    self.data_transformation_artifact
                    .transformed_object_file_path
                )
            )

            model_dir_path = os.path.dirname(
                self.model_trainer_config.trained_model_file_path
            )
            os.makedirs(model_dir_path, exist_ok=True)

            network_model = NetworkModel(
                preprocessor=preprocessor,
                model=best_model
            )
            save_object(
                self.model_trainer_config.trained_model_file_path,
                obj=network_model
            )

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=(
                    self.model_trainer_config.trained_model_file_path
                ),
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )

            logging.info(f"Model trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_train_file_path
            )
            test_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_test_file_path
            )

            x_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            x_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            model_trainer_artifact = self.train_model(
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test
            )

            logging.info("Model trainer completed successfully")

            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
