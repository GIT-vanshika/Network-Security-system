from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils import read_yaml_file, write_yaml_file

from scipy.stats import ks_2samp
import pandas as pd
import os
import sys


class DataValidation:

    def __init__(self,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):

        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            required_columns = len(self._schema_config["columns"])
            logging.info(f"Required columns: {required_columns}")
            logging.info(f"Dataframe columns: {len(dataframe.columns)}")

            return len(dataframe.columns) == required_columns

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    def is_numerical_column_exist(self, dataframe: pd.DataFrame) -> bool:
        try:
            numerical_columns = self._schema_config["numerical_columns"]

            missing_cols = [
                col for col in numerical_columns if col not in dataframe.columns
            ]

            if missing_cols:
                logging.info(f"Missing numerical columns: {missing_cols}")
                return False

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True
            report = {}

            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]

                stat, p_value = ks_2samp(d1, d2)

                drift_detected = p_value < threshold

                if drift_detected:
                    status = False

                report[column] = {
                    "p_value": float(p_value),
                    "drift_status": drift_detected
                }

            drift_report_file_path = self.data_validation_config.drift_report_file_path

            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)

            write_yaml_file(file_path=drift_report_file_path, content=report)

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_path = self.data_ingestion_artifact.trained_file_path
            test_path = self.data_ingestion_artifact.test_file_path

            train_df = self.read_data(train_path)
            test_df = self.read_data(test_path)

            # Column validation
            if not self.validate_number_of_columns(train_df):
                raise Exception("Train dataframe column mismatch")

            if not self.validate_number_of_columns(test_df):
                raise Exception("Test dataframe column mismatch")

            # Numerical validation
            if not self.is_numerical_column_exist(train_df):
                raise Exception("Missing numerical columns in train")

            if not self.is_numerical_column_exist(test_df):
                raise Exception("Missing numerical columns in test")

            # Drift detection
            status = self.detect_dataset_drift(train_df, test_df)

            # Save valid files
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)

            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)

            return DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)
