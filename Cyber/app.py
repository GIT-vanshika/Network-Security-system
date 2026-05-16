import os
import sys
from typing import Optional

import pandas as pd
import uvicorn

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Request,
    UploadFile,
    File,
)

from fastapi.responses import (
    HTMLResponse,
)

from fastapi.templating import Jinja2Templates

from pydantic import BaseModel, Field

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.pipeline.batch_prediction import BatchPrediction
from networksecurity.pipeline.training_pipeline import TrainingPipeline


PREDICTION_OUTPUT_PATH = os.path.join(
    "prediction_output",
    "output.csv"
)


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

    output_file_path: Optional[str] = Field(
        default=PREDICTION_OUTPUT_PATH,
        description="Exact prediction CSV path.",
    )


templates = Jinja2Templates(directory="template")


def render_prediction_table(file_path: str) -> str:

    dataframe = pd.read_csv(file_path)

    # LIMIT ROWS TO PREVENT BROWSER FREEZE
    dataframe = dataframe.head(50)

    return dataframe.to_html(
        classes="cyber-table",
        index=False,
        border=0,
        justify="center",
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):

    return templates.TemplateResponse(
        "table.html",
        {
            "request": request,
            "table": None,
            "input_file_path": "",
            "prediction_file_path": PREDICTION_OUTPUT_PATH,
            "message": "Run a batch prediction to view results.",
        },
    )


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

        return {
            "model_file_path": model_file_path
        }

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


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

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/predict")
def batch_predict(request: PredictionRequest):

    try:

        if not os.path.exists(request.input_file_path):

            raise FileNotFoundError(
                f"Input file not found: {request.input_file_path}"
            )

        if (
            request.model_file_path
            and not os.path.exists(request.model_file_path)
        ):

            raise FileNotFoundError(
                f"Model file not found: {request.model_file_path}"
            )

        batch_prediction = BatchPrediction(
            input_file_path=request.input_file_path,
            model_file_path=request.model_file_path,
            output_dir=request.output_dir,
            output_file_path=request.output_file_path,
        )

        prediction_file_path = batch_prediction.predict()

        return {
            "message": "Batch prediction completed successfully.",
            "prediction_file_path": prediction_file_path,
        }

    except NetworkSecurityException as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ================================
# CSV UPLOAD ENDPOINT
# ================================

@app.post("/upload-test-csv")
async def upload_test_csv(
    file: UploadFile = File(...)
):

    try:

        # CREATE UPLOADS FOLDER
        os.makedirs("uploads", exist_ok=True)

        # SAVE UPLOADED CSV
        uploaded_file_path = os.path.join(
            "uploads",
            file.filename
        )

        with open(uploaded_file_path, "wb") as f:
            f.write(await file.read())

        # RUN PREDICTION
        batch_prediction = BatchPrediction(
            input_file_path=uploaded_file_path,
            output_file_path=PREDICTION_OUTPUT_PATH
        )

        prediction_file_path = batch_prediction.predict()

        return {
            "message": "Prediction completed successfully",
            "prediction_output_file": prediction_file_path
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/predict-ui", response_class=HTMLResponse)
def batch_predict_ui(
    request: Request,

    input_file_path: str = Query(
        "valid_data/test.csv",
        description="CSV file path to use for prediction.",
    ),

    model_file_path: Optional[str] = Query(
        default=None,
        description="Optional trained model path.",
    ),

    output_file_path: str = Query(
        PREDICTION_OUTPUT_PATH,
        description="Prediction CSV output path.",
    ),
):

    try:

        if not os.path.exists(input_file_path):

            raise FileNotFoundError(
                f"Input file not found: {input_file_path}"
            )

        if (
            model_file_path
            and not os.path.exists(model_file_path)
        ):

            raise FileNotFoundError(
                f"Model file not found: {model_file_path}"
            )

        batch_prediction = BatchPrediction(
            input_file_path=input_file_path,
            model_file_path=model_file_path,
            output_file_path=output_file_path,
        )

        prediction_file_path = batch_prediction.predict()

        table = render_prediction_table(
            prediction_file_path
        )

        return templates.TemplateResponse(
            "table.html",
            {
                "request": request,
                "table": table,
                "input_file_path": input_file_path,
                "prediction_file_path": prediction_file_path,
                "message": "Batch prediction completed successfully.",
            },
        )

    except Exception as e:

        return templates.TemplateResponse(
            "table.html",
            {
                "request": request,
                "table": None,
                "input_file_path": input_file_path,
                "prediction_file_path": output_file_path,
                "message": str(e),
            },
            status_code=500,
        )


@app.get("/prediction-output", response_class=HTMLResponse)
def prediction_output(request: Request):

    try:

        if not os.path.exists(PREDICTION_OUTPUT_PATH):

            raise FileNotFoundError(
                f"Prediction output not found: {PREDICTION_OUTPUT_PATH}"
            )

        table = render_prediction_table(
            PREDICTION_OUTPUT_PATH
        )

        return templates.TemplateResponse(
            "table.html",
            {
                "request": request,
                "table": table,
                "input_file_path": "",
                "prediction_file_path": PREDICTION_OUTPUT_PATH,
                "message": "Showing latest prediction output.",
            },
        )

    except Exception as e:

        return templates.TemplateResponse(
            "table.html",
            {
                "request": request,
                "table": None,
                "input_file_path": "",
                "prediction_file_path": PREDICTION_OUTPUT_PATH,
                "message": str(e),
            },
            status_code=404,
        )


if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )