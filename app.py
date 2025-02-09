from fastapi import FastAPI
from pydantic import BaseModel
from collectFeedback import getRatings, getMetrics
import collectFeedback
import uvicorn
from typing import List, Union


# class User_Input(BaseModel):
#     user: str

class Item(BaseModel):
    user_id: str
    product_id: str
    feedback: str
class Item_List(BaseModel):
    i: Item

class User_Input(BaseModel):
    integers: List[Union[int]]


app = FastAPI()


@app.post("/collectFeedback")
def send(inp: List[Item]):
    user_feedback = []
    for i in inp:
        d = {"user_id": i.user_id, "product_id": i.product_id, "feedback": i.feedback}
        user_feedback.append(d)
    print(user_feedback)
    result = collectFeedback.getRatings(user_feedback)
    return result

@app.post("/collectMetrics")
def send(inp: User_Input):
    print(inp)
    l = [i for i in inp.integers]
    print(l)
    metric = []
    d = {'Mean Reciprocal Rank':(l[0]/100)}
    metric.append(d)
    print(metric)
    d = {'Coversion':l[1]}
    metric.append(d)
    count=0
    for x in l[2:]:
        count+=1
        d = {'Product'+str(count):x}
        metric.append(d)
    result = collectFeedback.getMetrics(metric)
    return result
# uvicorn app:app --reload 
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)