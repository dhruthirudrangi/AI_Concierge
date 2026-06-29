from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.recommend import router as recommend_router
from app.routers.benchmark import router as benchmark_router
from app.routers.integration import router as integration_router
from app.services.semantic_service import EmbeddingService



from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager

async def lifespan(app: FastAPI):
    # Pre-initialize the Sentence Transformer model singleton on startup to prevent request-level cold starts
    print("Pre-loading Sentence Transformer model...")
    EmbeddingService.get_model()
    yield
    print("Application shutdown complete.")


app = FastAPI(
    title="AI-Powered Credit Card Recommendation System",
    description="Vector Search, TF-IDF and Transformer-based hybrid credit card recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "AI-Powered Credit Card Recommendation System Running Successfully"}


app.include_router(recommend_router)
app.include_router(benchmark_router)
app.include_router(integration_router)