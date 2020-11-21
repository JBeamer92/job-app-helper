from fastapi import FastAPI
from typing import Optional

app = FastAPI()


@app.get("/")
async def home():
    return "I'm Ready!"


@app.get("/apps")
async def get_apps():
    return [{
        "company": "Anthem",
        "position": "Developer",
    }, {
        "company": "Kindred",
        "position": "Programmer Analyst",
    }]


@app.get('/items/{item_id}')
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
