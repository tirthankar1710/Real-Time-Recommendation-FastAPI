from fastapi import FastAPI, BackgroundTasks

from pathlib import Path
from datetime import datetime

from src.utils import read_yaml, upload_json_to_s3
from src.prediction import load_model,PredictionPipeline

app = FastAPI()

prediction_pipeline = None

@app.on_event("startup")
def startup_load_model():
    global prediction_pipeline
    config_path = Path("src/config.yaml")
    load_model(config_file_path=config_path)
    prediction_pipeline = PredictionPipeline(config_path="src/config.yaml")
    return {"Status": "Model Loaded and Prediction Pipeline Initialized"}

@app.get("/")
def read_root():
    return {"Status": "Running!"}

@app.get("/reload_model")
def reload_model(job_id = None):
    try:
        global prediction_pipeline
        config_path = Path("src/config.yaml")
        load_model(config_file_path=config_path, job_id=job_id)
        prediction_pipeline = PredictionPipeline(config_path="src/config.yaml")
    except Exception as e:
        return {
            "Error": e
        }
    return {"Status": f"Model Reload Completed for job-id: {job_id}!"}

@app.get("/prediction")
def get_prediction(user_id, parent_asin):
    # prediction_pipeline = PredictionPipeline(config_path="src/config.yaml") # For Local
    global prediction_pipeline
    recommendations = prediction_pipeline.get_hybrid_recommendations(
        user_id=user_id, 
        parent_asin=parent_asin
        )
    return recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)