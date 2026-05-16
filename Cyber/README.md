# Network Security ML Pipeline

Production-grade machine learning system for phishing detection in network security. This project implements an end-to-end ML pipeline with data ingestion, validation, transformation, model training, and batch prediction capabilities.

## Overview

The Network Security ML Pipeline is designed to identify malicious URLs using machine learning. It processes network data to classify URLs as either phishing threats or legitimate websites. The system handles the complete ML lifecycle including data collection, validation, preprocessing, model training, and prediction serving through a REST API.

## Key Features

- **Data Management**: Automated data ingestion from MongoDB with feature store management
- **Data Validation**: Schema validation, numerical checks, and drift detection using Kolmogorov-Smirnov test
- **Data Transformation**: KNN-based imputation and preprocessing pipeline
- **Model Training**: Support for multiple ML algorithms with cross-validation
- **REST API**: FastAPI-based endpoint for real-time predictions and batch processing
- **Containerization**: Docker and Docker Compose for development and production deployment
- **CI/CD Integration**: GitHub Actions workflow for automated testing and deployment
- **Logging & Monitoring**: Comprehensive logging and MLflow experiment tracking
- **Testing**: Pytest-based test suite with coverage reporting

## Project Status

| Component | Status | Details |
|-----------|--------|---------|
| Data Ingestion | Complete | MongoDB integration with feature store |
| Data Validation | Complete | Schema validation and drift detection |
| Data Transformation | Complete | KNN imputation and preprocessing |
| Model Training | Complete | Multiple algorithm support with evaluation |
| Prediction Pipeline | Complete | Batch and real-time prediction endpoints |
| FastAPI Server | Complete | REST API with interactive documentation |
| Docker Setup | Complete | Development and production configurations |
| CI/CD Pipeline | Complete | GitHub Actions workflows |
| Code Quality | Complete | Linting and formatting enforced |

## Technology Stack

- Python 3.10
- FastAPI - REST API framework
- MongoDB - Database management
- Scikit-learn - Machine learning algorithms
- Pandas - Data manipulation and analysis
- NumPy - Numerical computing
- PyYAML - Configuration management
- MLflow - Experiment tracking
- Docker - Containerization
- GitHub Actions - CI/CD automation

## Project Structure

```
Cyber/
├── .github/
│   └── workflows/              # GitHub Actions CI/CD
│       ├── ci-cd.yml           # Build, test, push to registry
│       └── deploy.yml          # Production deployment
│
├── networksecurity/            # Main package
│   ├── components/             # Pipeline components
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_tranformation.py
│   │   └── model_trainer.py
│   ├── constants/              # Configuration constants
│   ├── entity/                 # Data classes
│   ├── exception/              # Custom exceptions
│   ├── logging/                # Logging setup
│   ├── pipeline/               # Pipeline orchestration
│   ├── utils/                  # Helper utilities
│   └── data_schema/            # YAML schema
│
├── Network_Data/               # Training datasets
├── Artifacts/                  # Pipeline outputs
├── logs/                       # Application logs
├── mlruns/                     # MLflow tracking
├── prediction_output/          # Prediction results
│
├── app.py                      # FastAPI application
├── main.py                     # Training pipeline entry
├── Dockerfile                  # Development image
├── Dockerfile.prod             # Production image
├── docker-compose.yml          # Local environment
├── docker-compose.prod.yml     # Production environment
├── Makefile                    # Development commands
├── requirements.txt            # Python dependencies
├── setup.py                    # Package configuration
├── pytest.ini                  # Test configuration
└── README.md                   # This file
```

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- MongoDB (included in Docker Compose)
- Git

## Installation

### Option 1: Local Development Setup

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd Cyber_security_ML/Cyber

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Option 2: Docker Deployment

```bash
cd Cyber_security_ML/Cyber

# Development environment
docker-compose up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d
```

## Quick Start

### 1. Start Services

```bash
# Using Docker Compose
docker-compose up -d

# Or using Make
make docker-compose-up
```

### 2. Upload Training Data

```bash
python push_data.py
```

### 3. Run Training Pipeline

```bash
python main.py

# Or using Make
make run
```

### 4. Access API

- Interactive API Documentation: http://localhost:8000/docs
- Alternative Documentation: http://localhost:8000/redoc
- Health Check: http://localhost:8000/

## Usage

### Training Pipeline

Execute the complete training pipeline:

```bash
python main.py
```

This will:
1. Ingest data from MongoDB
2. Validate data against schema
3. Transform and preprocess data
4. Train machine learning models
5. Evaluate and select best model
6. Save artifacts and logs

### REST API Endpoints

#### Health Check
```bash
curl http://localhost:8000/
```

#### Batch Prediction
```bash
curl -X POST http://localhost:8000/predict/batch \
  -F "input_file_path=Network_Data/Phishing_Legitimate_full.csv"
```

#### Interactive Documentation
Open http://localhost:8000/docs in your browser for Swagger UI with try-it-out capabilities.

### Development Commands

Available Make commands:

```bash
make help              # Show all commands
make install           # Install production dependencies
make install-dev       # Install development dependencies
make test              # Run tests with coverage
make lint              # Run linting checks
make format            # Format code
make build             # Build package
make run               # Run FastAPI server locally
make docker-build      # Build Docker image
make docker-compose-up # Start Docker Compose services
make docker-compose-down # Stop Docker Compose services
make ci-local          # Run local CI pipeline (lint -> test)
```

## Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Key environment variables:

```
MONGO_DB_URL=mongodb://admin:admin123@mongo:27017
PYTHONUNBUFFERED=1
APP_HOST=0.0.0.0
APP_PORT=8000
```

### Data Schema

Define dataset structure in `networksecurity/data_schema/schema.yml`:

```yaml
column_name:
  required: true
  type: numeric
  min: 0
  max: 1
```

### Pipeline Constants

Configure pipeline behavior in `networksecurity/constants/training_pipeline/__init__.py`:

```python
TARGET_COLUMN = "CLASS_LABEL"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 0.2
MODEL_TRAINER_EXPECTED_SCORE = 0.6
```

## Testing

Run the test suite:

```bash
# All tests with coverage
make test

# Specific test file
pytest tests/test_data_ingestion.py -v

# With coverage report
pytest --cov=networksecurity --cov-report=html
```

View HTML coverage report:
```bash
open htmlcov/index.html
```

## Code Quality

### Linting

```bash
make lint
```

Checks code style against PEP 8 with flake8.

### Formatting

```bash
make format
```

Automatically formats code with Black and sorts imports with isort.

### Type Checking

```bash
mypy networksecurity --ignore-missing-imports
```

## Continuous Integration

GitHub Actions automatically runs on every push:

1. Code linting with flake8
2. Test suite with pytest and coverage
3. Docker image build
4. Push to GitHub Container Registry

View workflows in `.github/workflows/`:
- `ci-cd.yml` - Build and test pipeline
- `deploy.yml` - Production deployment

## Docker Deployment

### Development

```bash
docker-compose up -d

# Services available:
# - API: http://localhost:8000
# - MongoDB: localhost:27017
# - MongoDB Express: http://localhost:8081
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Production configuration includes:
- Multi-stage Docker build for optimized image size
- Resource limits and reservations
- Health checks
- Auto-restart policies

See `DOCKER_GUIDE.md` for detailed Docker documentation.

## Troubleshooting

### MongoDB Connection Error

Ensure MongoDB service is running:
```bash
docker-compose ps mongo
docker-compose logs mongo
```

### Port Already in Use

Change port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Map to different port
```

### Missing Dependencies

Reinstall dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

## Performance Metrics

The system tracks performance using:

- Coverage Reports: `htmlcov/index.html`
- MLflow Experiments: http://localhost:5000 (when running)
- Application Logs: `logs/` directory
- Artifacts: `Artifacts/` directory with timestamped outputs

## Security Considerations

- Environment variables for sensitive configuration
- MongoDB authentication enabled by default
- Non-root Docker user in production
- Health checks for service readiness
- Proper exception handling and logging

## Development Workflow

1. Create feature branch
2. Make changes and run local tests: `make ci-local`
3. Commit and push to trigger CI/CD
4. GitHub Actions runs full test suite
5. Merge after successful CI/CD

## License

This project is proprietary and confidential.

## Support

For issues, questions, or contributions, please contact the development team.

## Changelog

### Version 1.0.0 (May 2026)
- Complete ML pipeline implementation
- FastAPI REST endpoints
- Docker containerization
- GitHub Actions CI/CD
- Full test coverage
- PEP 8 code compliance
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
