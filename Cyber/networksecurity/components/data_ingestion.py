from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Config
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import numpy as np
import pandas as pd
import pymongo

from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")


class DataIngestion:

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    # Step 1: Extract data from MongoDB
    # ==============================
    def export_collection_as_dataframe(self) -> pd.DataFrame:
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)

            collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))

            # Drop MongoDB ID column
            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)

            # Replace "na" with actual NaN
            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    # Step 2: Save raw data (Feature Store)
    # ==============================
    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path

            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            dataframe.to_csv(feature_store_file_path, index=False, header=True)

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    # Step 3: Train-Test Split
    # ==============================
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio
            )

            logging.info("Performed train-test split on dataframe")

            # Create directory for train/test
            dir_path = os.path.dirname(
                self.data_ingestion_config.training_file_path
            )
            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train and test datasets")

            # Save train file
            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False,
                header=True
            )

            # Save test file
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False,
                header=True
            )

            logging.info("Train and test files saved successfully")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==============================
    # Final Pipeline Trigger
    # ==============================
    def initiate_data_ingestion(self):
        try:
            # Step 1: Extract
            dataframe = self.export_collection_as_dataframe()

            # Step 2: Save raw data
            dataframe = self.export_data_into_feature_store(dataframe)

            # Step 3: Split
            self.split_data_as_train_test(dataframe)

            dataingestionartifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
