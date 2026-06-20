# Network Security ML Pipeline

An end-to-end machine learning project for detecting phishing URLs using a modular, production-style pipeline. The system trains on URL and webpage behavior features, selects the best classification model, saves reusable artifacts, and exposes prediction through a FastAPI application.

## Problem Statement

Phishing websites are one of the most common causes of credential theft, fraud, malware delivery, and data breaches. In industry, security teams cannot manually verify every URL coming from emails, chats, forms, tickets, and web traffic. This project solves that problem by using machine learning to classify URLs as phishing or legitimate based on their structural and behavioral features.

## Industry Use Case

This project can support security teams by automatically analyzing suspicious URLs and helping reduce:

- Credential theft from fake login pages
- Financial fraud through malicious links
- Malware infection from unsafe websites
- Manual workload for SOC and security analysts
- Delayed response to phishing campaigns

In its current form, the project supports batch prediction using structured CSV input. In a real company, it can be extended with a feature extraction layer that accepts raw URLs, extracts the required features, and sends them to the prediction API.

## Dataset

The project uses `Network_Data/Phishing_Legitimate_full.csv`, a phishing URL dataset with around 10,000 URL records and about 50 numerical features, including the target column `CLASS_LABEL`.

The features describe URL and webpage patterns such as:

- URL length
- Number of dots, dashes, query parameters, and numeric characters
- HTTPS availability
- IP address usage
- Suspicious form actions
- External hyperlinks and resources
- Iframe or frame usage
- Missing title and popup behavior

These features are useful because phishing websites often show abnormal URL structures and suspicious page behavior compared to legitimate websites.

## Learning Type

This project is an example of **offline learning**. The model is trained on a fixed dataset, saved as a model artifact, and later used for prediction. It does not automatically update after every new URL. When new data becomes available, the training pipeline can be rerun and the updated model can be redeployed.

## Project Architecture

```text
Raw CSV dataset
    |
    v
push_data.py
    |
    v
MongoDB
    |
    v
Data Ingestion
    |
    v
Data Validation
    |
    v
Data Transformation
    |
    v
Model Training
    |
    v
Saved Model Artifacts
    |
    v
FastAPI Prediction Service
    |
    v
Prediction Output CSV
```

## Pipeline Stages and Data Flow

### 1. Data Upload

File: `push_data.py`

The source CSV is converted into JSON-like records and inserted into MongoDB. This was done because real industry systems usually read data from databases or data stores instead of directly depending on a local CSV file.

### 2. Data Ingestion

File: `networksecurity/components/data_ingestion.py`

The ingestion stage reads records from MongoDB, converts them into a Pandas DataFrame, removes MongoDB's `_id` column, replaces `"na"` values with `NaN`, saves raw data into a feature store, and splits the dataset into training and testing files.

Why this stage is needed:

- To collect data from a database source
- To create a reproducible raw feature store
- To split data into train and test sets for proper evaluation

### 3. Data Validation

File: `networksecurity/components/data_validation.py`

The validation stage checks whether the train and test files match the expected schema from `networksecurity/data_schema/schema.yml`. It validates the number of columns, checks required numerical columns, and performs data drift detection using the Kolmogorov-Smirnov test.

Why this stage is needed:

- To prevent training on incorrect or incomplete data
- To ensure the incoming data structure matches the model expectation
- To detect whether train and test distributions are significantly different

Why KS test:

The Kolmogorov-Smirnov test compares two distributions. It helps identify data drift by checking whether train and test feature distributions are statistically different.

### 4. Data Transformation

File: `networksecurity/components/data_tranformation.py`

The transformation stage separates input features from the target column `CLASS_LABEL`, removes the `id` column, replaces target value `-1` with `0`, applies `KNNImputer` to handle missing values, and saves transformed train/test arrays as NumPy files. It also saves the preprocessing object for later prediction.

Why this stage is needed:

- To prepare clean numerical input for ML algorithms
- To remove non-predictive identifiers such as `id`
- To make training and prediction use the same preprocessing logic

Why KNNImputer:

KNN imputation fills missing values using similar neighboring records. It is more context-aware than simple mean or median imputation.

### 5. Model Training

File: `networksecurity/components/model_trainer.py`

The model trainer loads transformed arrays and trains multiple classification algorithms:

- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosting
- AdaBoost

The project compares models using F1 score, performs hyperparameter tuning using GridSearchCV, checks train-test performance gap to avoid overfitting, tracks metrics with MLflow, and saves the best model.

Why multiple models:

Different algorithms learn patterns differently. Instead of assuming one model is best, the project trains multiple models and selects the best one based on evaluation.

### 6. Batch Prediction

File: `networksecurity/pipeline/batch_prediction.py`

The prediction pipeline loads the latest trained model, reads an input CSV file, removes the target column if present, applies the saved preprocessing, predicts phishing or legitimate labels, and writes a new output CSV with a `prediction` column.

### 7. API Service

File: `app.py`

FastAPI exposes the model through REST endpoints and a simple UI.

Important endpoints:

- `GET /health` - service health check
- `GET /latest-model` - returns latest trained model path
- `POST /train` - runs the full training pipeline
- `POST /predict` - runs batch prediction from a CSV path
- `POST /upload-test-csv` - uploads a CSV and runs prediction
- `GET /predict-ui` - browser-based prediction view
- `GET /prediction-output` - shows latest prediction output

## Evaluation Metrics

This project uses F1 score, precision, and recall because phishing detection is a security-sensitive classification problem.

### Precision

Precision answers: out of all URLs predicted as phishing, how many were actually phishing?

High precision helps reduce false alarms, so legitimate websites are not incorrectly blocked too often.

### Recall

Recall answers: out of all actual phishing URLs, how many did the model catch?

High recall is important because missing a phishing URL can lead to credential theft, fraud, or malware infection.

### F1 Score

F1 score is the harmonic mean of precision and recall. It is useful when both false positives and false negatives matter. Accuracy alone can be misleading, especially if the dataset is imbalanced.

### Logged Model Performance

One of the best logged runs selected **Gradient Boosting** as the best model.

| Dataset | F1 Score | Precision | Recall |
|---|---:|---:|---:|
| Train | 0.9939 | 0.9929 | 0.9949 |
| Test | 0.9843 | 0.9815 | 0.9872 |

These scores show that the model performed strongly on unseen test data and was not only memorizing the training data.

## Hyperparameter Tuning

Hyperparameter tuning was used because the same algorithm can perform differently depending on settings such as:

- Number of estimators
- Learning rate
- Tree criterion
- Subsample ratio

The project uses **GridSearchCV** because it systematically tries parameter combinations with cross-validation and selects the best-performing configuration. This is better than manually guessing parameters because it gives a more reliable and optimized model selection process.

## Why Docker Was Used

Docker was used to package the application, dependencies, runtime environment, and service configuration into containers. This makes the project easier to run on different machines and closer to industry deployment.

Docker Compose starts:

- FastAPI application on port `8000`
- MongoDB on port `27017`
- Mongo Express on port `8081`

## How a Company Can Use It

Current usage:

1. Start the services using Docker Compose.
2. Upload or provide a CSV file with the required feature columns.
3. Call the prediction API.
4. Receive an output CSV with phishing/legitimate predictions.

Example:

```bash
docker-compose up -d
```

API docs:

```text
http://localhost:8000/docs
```

Prediction UI:

```text
http://localhost:8000/predict-ui
```

In a real production environment, this API can be integrated with:

- Email gateways
- Browser security tools
- SOC dashboards
- Web proxy logs
- Threat intelligence systems

## Trade-Offs and Limitations

The current project is strong from an ML pipeline and deployment architecture perspective, but it is not yet a fully automatic real-time phishing detection system.

Current limitations:

- Prediction expects structured CSV features, not raw URLs
- No live URL monitoring yet
- No automatic feature extraction service yet
- No real-time alerting workflow yet
- Model retraining is offline, not continuous

Possible future improvements:

- Add raw URL feature extraction
- Add a real-time prediction endpoint that accepts a URL directly
- Connect with email or browser security systems
- Add monitoring for model drift in production
- Add scheduled retraining
- Add alerting and analyst feedback loop

## Most Difficult Part

The most difficult part of building this project was understanding the modular pipeline architecture. This was different from writing everything in one notebook or one script. It required understanding why separate files are needed for configs, artifacts, components, pipelines, constants, utilities, logging, and exception handling.

The key learning was that each file has a clear responsibility:

- Config files define paths and settings
- Component files perform the actual work
- Artifact files pass outputs from one stage to the next
- Pipeline files connect all stages in order
- Utility files avoid repeated code
- Logging and exception files make debugging easier

This modular structure makes the project more maintainable, reusable, debuggable, and closer to how ML systems are built in industry.

## Technology Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- SciPy
- PyYAML
- MongoDB
- FastAPI
- Uvicorn
- MLflow
- Docker
- Docker Compose
- GitHub Actions
- Pytest

## Project Structure

```text
Cyber/
  app.py
  main.py
  push_data.py
  requirements.txt
  setup.py
  Dockerfile
  docker-compose.yml
  Network_Data/
    Phishing_Legitimate_full.csv
  final_model/
    model.pkl
    preprocessor.pkl
  prediction_output/
  networksecurity/
    components/
      data_ingestion.py
      data_validation.py
      data_tranformation.py
      model_trainer.py
    constants/
      training_pipeline/
        __init__.py
    data_schema/
      schema.yml
    entity/
      artifact_entity.py
      config_entity.py
    exception/
      exception.py
    logging/
      logger.py
    pipeline/
      batch_prediction.py
      training_pipeline.py
    utils/
      main_utils.py
```

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

Create a `.env` file:

```env
MONGO_DB_URL=mongodb://admin:admin123@localhost:27017
```

Push data to MongoDB:

```bash
python push_data.py
```

Run training:

```bash
python main.py
```

Run API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Docker Setup

Start all services:

```bash
docker-compose up -d
```

Stop all services:

```bash
docker-compose down
```

Available services:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- MongoDB: `localhost:27017`
- Mongo Express: `http://localhost:8081`

## CI/CD

GitHub Actions workflows are included under `.github/workflows/` for testing, building, and deployment automation.

## Summary

This project demonstrates a complete ML lifecycle for phishing URL detection: data ingestion, validation, transformation, model training, metric tracking, prediction serving, Docker deployment, and production-style modular coding.
