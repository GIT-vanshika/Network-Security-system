# Network Security ML Pipeline

This project builds a machine learning pipeline for network security data, focused on phishing URL detection. It extracts phishing/legitimate URL feature data, stores and reads data through MongoDB, creates training artifacts, validates the dataset schema, and checks for dataset drift before the data moves further into model training.

## Project Objective

The goal is to create an end-to-end, modular ML workflow for detecting suspicious or phishing URLs from structured URL features. The current pipeline prepares reliable train/test data and validates that incoming data matches the expected schema before model development and deployment steps are added.

## Current Features

- Upload raw CSV data into MongoDB using `push_data.py`.
- Ingest data from MongoDB into the local feature store.
- Split ingested data into train and test datasets.
- Validate train/test files against the configured schema in `networksecurity/data_schema/schema.yml`.
- Check for numerical column availability.
- Detect dataset drift between train and test data using the Kolmogorov-Smirnov test.
- Save pipeline artifacts under the `Artifacts/` directory.
- Log pipeline execution under the `logs/` directory.

## Project Progress

| Stage | Status | Notes |
| --- | --- | --- |
| Project structure | Completed | Modular package layout is available under `networksecurity/`. |
| Data source setup | Completed | Source CSV and MongoDB upload script are available. |
| Data ingestion | Completed | Data is extracted from MongoDB, saved to feature store, and split into train/test files. |
| Data validation | Completed | Schema validation, numerical column checks, and drift report generation are implemented. |
| Model training | Pending | Training component is not implemented yet. |
| Model evaluation | Pending | Evaluation metrics and model selection are not implemented yet. |
| Prediction pipeline | Pending | Inference workflow is not implemented yet. |
| Deployment | Pending | Dockerfile exists but deployment setup is not completed. |

## Repository Structure

```text
networksecurity/
  components/          # Pipeline components such as ingestion and validation
  constants/           # Pipeline constants
  data_schema/         # Dataset schema definition
  entity/              # Config and artifact entities
  exception/           # Custom exception handling
  logging/             # Logging setup
  pipeline/            # Pipeline package placeholder
  utils/               # YAML and utility helpers

Network_Data/          # Source dataset
Artifacts/             # Generated pipeline artifacts
logs/                  # Runtime logs
main.py                # Runs ingestion and validation pipeline
push_data.py           # Pushes CSV records into MongoDB
requirements.txt       # Python dependencies
setup.py               # Package setup
```

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Add MongoDB connection details in a `.env` file.

```env
MONGO_DB_URL=your_mongodb_connection_string
```

## Usage

To upload the source CSV data into MongoDB:

```bash
python push_data.py
```

To run the current training pipeline stages:

```bash
python main.py
```

The pipeline writes generated files into a timestamped folder under `Artifacts/`.

## Next Steps

- Add data transformation and preprocessing.
- Implement model training for phishing URL classification.
- Add model evaluation and metric tracking.
- Build a prediction pipeline.
- Complete Docker and deployment configuration.
- Add automated tests for ingestion and validation components.
