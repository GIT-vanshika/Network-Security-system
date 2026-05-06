import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    TrainingPipelineConfig
)


if __name__ == "__main__":
    try:
        # ==============================
        # Step 1: Training Pipeline Config
        # ==============================
        trainingPipelineConfig = TrainingPipelineConfig()

        # ==============================
        # Step 2: Data Ingestion
        # ==============================
        dataIngestionConfig = DataIngestionConfig(trainingPipelineConfig)

        data_ingestion = DataIngestion(dataIngestionConfig)

        logging.info("Starting data ingestion process")

        dataingestionartifact = data_ingestion.initiate_data_ingestion()

        print("\nData Ingestion Output:")
        print(dataingestionartifact)

        # ==============================
        # Step 3: Data Validation
        # ==============================
        dataValidationConfig = DataValidationConfig(trainingPipelineConfig)

        data_validation = DataValidation(
            data_ingestion_artifact=dataingestionartifact,
            data_validation_config=dataValidationConfig
        )

        logging.info("Starting data validation process")

        data_validation_artifact = data_validation.initiate_data_validation()

        print("\nData Validation Output:")
        print(data_validation_artifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)