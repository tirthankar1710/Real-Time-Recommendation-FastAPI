from fastapi import FastAPI, BackgroundTasks
import pandas as pd
from surprise import dump

app = FastAPI()


# Need to fetch model artifacts on start up 
# Need to fetch on reload based.
# something

@app.get("/")
def read_root():
    return {"Status": "Running!"}

@app.get("/test_function")
def read_root_2():
    return {"Status": "Test Function Running!"}

# adding comment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)