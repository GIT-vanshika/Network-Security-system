import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig


if __name__ == "__main__":
    try:
        trainingPipelineConfig = TrainingPipelineConfig()

        dataIngestionConfig = DataIngestionConfig(trainingPipelineConfig)

        data_ingestion = DataIngestion(dataIngestionConfig)

        logging.info("Starting data ingestion process")

        dataingestionartifact = data_ingestion.initiate_data_ingestion()

        print(dataingestionartifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)