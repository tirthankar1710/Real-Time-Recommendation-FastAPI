from fastapi import FastAPI, BackgroundTasks

from pathlib import Path

from src.utils import read_yaml
from src.prediction import load_model,PredictionPipeline

prediction_pipeline = PredictionPipeline(config_path="src/config.yaml")

app = FastAPI()


@app.on_event("startup")
def startup_load_model():
    config_path = Path("src/config.yaml")
    load_model(config_file_path=config_path)
    return {"Status": "Test Function Running!"}

@app.get("/")
def read_root():
    return {"Status": "Running!"}

@app.post("/reload_model")
def reload_model():
    config_path = Path("src/config.yaml")
    load_model(config_file_path=config_path)

@app.get("/prediction")
def get_prediction(user_id, parent_asin):
    recommendations = prediction_pipeline.get_hybrid_recommendations(
        user_id=user_id, 
        parent_asin=parent_asin
        )
    return recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)