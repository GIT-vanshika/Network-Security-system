import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils import load_object

PREDICTION_COLUMN = "prediction"
DEFAULT_OUTPUT_DIR = "prediction_output"


class BatchPrediction:
    def __init__(
        self,
        input_file_path: str,
        model_file_path: str = None,
        output_dir: str = DEFAULT_OUTPUT_DIR,
    ):
        try:
            self.input_file_path = input_file_path
            self.model_file_path = model_file_path or self.get_latest_model_path()
            self.output_dir = output_dir
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def get_latest_model_path() -> str:
        try:
            model_paths = list(Path("Artifacts").glob("*/model_trainer/trained_model/model.pkl"))

            if not model_paths:
                raise FileNotFoundError(
                    "No trained model found under "
                    "Artifacts/*/model_trainer/trained_model/model.pkl"
                )

            latest_model_path = max(model_paths, key=lambda path: path.stat().st_mtime)
            return str(latest_model_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def get_prediction_features(dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            if TARGET_COLUMN in dataframe.columns:
                return dataframe.drop(columns=[TARGET_COLUMN], axis=1)

            return dataframe.copy()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def save_prediction_file(self, dataframe: pd.DataFrame) -> str:
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
            output_file_path = os.path.join(
                self.output_dir,
                f"prediction_{timestamp}.csv",
            )

            dataframe.to_csv(output_file_path, index=False, header=True)
            return output_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict(self) -> str:
        try:
            logging.info("Entered batch prediction pipeline")
            logging.info(f"Input file path: {self.input_file_path}")
            logging.info(f"Model file path: {self.model_file_path}")

            dataframe = self.read_data(self.input_file_path)
            prediction_features = self.get_prediction_features(dataframe)

            model = load_object(self.model_file_path)
            predictions = model.predict(prediction_features)

            prediction_dataframe = dataframe.copy()
            prediction_dataframe[PREDICTION_COLUMN] = predictions

            output_file_path = self.save_prediction_file(prediction_dataframe)

            logging.info(f"Batch prediction file saved at: {output_file_path}")
            return output_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys)


def parse_args():
    parser = argparse.ArgumentParser(description="Run batch prediction on a CSV file.")
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--model-file",
        default=None,
        help=(
            "Path to the trained NetworkModel pickle. If omitted, the latest "
            "model under Artifacts is used."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where the prediction CSV will be saved.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    batch_prediction = BatchPrediction(
        input_file_path=args.input_file,
        model_file_path=args.model_file,
        output_dir=args.output_dir,
    )
    prediction_file_path = batch_prediction.predict()

    print(f"Prediction file saved at: {prediction_file_path}")
