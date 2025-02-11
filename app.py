from fastapi import FastAPI
from pathlib import Path

from src.prediction import load_model,PredictionPipeline
from src.collectFeedback import getRatings, getMetrics
from src.logging_util import logger

from typing import List, Union
from pydantic import BaseModel

class Item(BaseModel):
    user_id: str
    product_id: str
    feedback: str
class Item_List(BaseModel):
    i: Item

class User_Input(BaseModel):
    integers: List[Union[int]]

app = FastAPI()

prediction_pipeline = None
config_path = Path("src/config.yaml")
load_model(config_file_path=config_path, job_id=None)
prediction_pipeline = PredictionPipeline(config_path="src/config.yaml")

@app.get("/")
def read_root():
    return {"Status": "Running!"}

@app.get("/reload_model")
def reload_model(job_id):
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

@app.post("/collectFeedback")
def send(inp: List[Item]):
    user_feedback = []
    for i in inp:
        d = {"user_id": i.user_id, "product_id": i.product_id, "feedback": i.feedback}
        user_feedback.append(d)
    result = getRatings(user_feedback)
    return result

@app.post("/collectMetrics")
def send(inp: User_Input):
    logger.info(inp)
    l = [i for i in inp.integers]
    logger.info(l)
    metric = []
    d = {'Mean Reciprocal Rank':(l[0]/100)}
    metric.append(d)
    logger.info(metric)
    d = {'Coversion':l[1]}
    metric.append(d)
    count=0
    for x in l[2:]:
        count+=1
        d = {'Product'+str(count):x}
        metric.append(d)
    result = getMetrics(metric)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)