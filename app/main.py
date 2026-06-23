from fastapi import FastAPI
from app.routers.recommend import router as recommend_router

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Crowd Violence Backend Running Successfully"}


app.include_router(recommend_router)