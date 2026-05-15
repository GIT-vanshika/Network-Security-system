import os
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.pipeline.batch_prediction import BatchPrediction
from networksecurity.pipeline.training_pipeline import TrainingPipeline


app = FastAPI(
    title="Network Security ML API",
    description="API for training the phishing detection pipeline and running batch predictions.",
    version="1.0.0",
)


class PredictionRequest(BaseModel):
    input_file_path: str = Field(
        ...,
        description="Path to the input CSV file for batch prediction.",
        examples=["Network_Data/Phishing_Legitimate_full.csv"],
    )
    model_file_path: Optional[str] = Field(
        default=None,
        description="Optional path to a trained NetworkModel pickle file.",
    )
    output_dir: str = Field(
        default="prediction_output",
        description="Directory where the prediction CSV should be saved.",
    )


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "network-security-ml",
    }


@app.get("/latest-model")
def get_latest_model():
    try:
        model_file_path = BatchPrediction.get_latest_model_path()
        return {"model_file_path": model_file_path}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/train")
def train_pipeline():
    try:
        training_pipeline = TrainingPipeline()
        model_trainer_artifact = training_pipeline.run_pipeline()

        return {
            "message": "Training pipeline completed successfully.",
            "trained_model_file_path": (
                model_trainer_artifact.trained_model_file_path
            ),
            "train_metrics": {
                "f1_score": model_trainer_artifact.train_metric_artifact.f1_score,
                "precision_score": (
                    model_trainer_artifact.train_metric_artifact.precision_score
                ),
                "recall_score": (
                    model_trainer_artifact.train_metric_artifact.recall_score
                ),
            },
            "test_metrics": {
                "f1_score": model_trainer_artifact.test_metric_artifact.f1_score,
                "precision_score": (
                    model_trainer_artifact.test_metric_artifact.precision_score
                ),
                "recall_score": (
                    model_trainer_artifact.test_metric_artifact.recall_score
                ),
            },
        }
    except NetworkSecurityException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
def batch_predict(request: PredictionRequest):
    try:
        if not os.path.exists(request.input_file_path):
            raise FileNotFoundError(
                f"Input file not found: {request.input_file_path}"
            )

        if request.model_file_path and not os.path.exists(request.model_file_path):
            raise FileNotFoundError(
                f"Model file not found: {request.model_file_path}"
            )

        batch_prediction = BatchPrediction(
            input_file_path=request.input_file_path,
            model_file_path=request.model_file_path,
            output_dir=request.output_dir,
        )
        prediction_file_path = batch_prediction.predict()

        return {
            "message": "Batch prediction completed successfully.",
            "prediction_file_path": prediction_file_path,
        }
    except NetworkSecurityException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
