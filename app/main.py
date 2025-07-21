from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.routers import auth, links, analytics, redirect

app = FastAPI(
    title="SnapShort API",
    description="Serverless URL shortener with analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(links.router, prefix="/links", tags=["Links"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(redirect.router, tags=["Redirect"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "snapshort"}


handler = Mangum(app, lifespan="off")
