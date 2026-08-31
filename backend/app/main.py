from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth_routes, demo_routes, misc_routes, path_routes, profile, skill_graph_routes
from app.core.config import get_settings
from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="SkillGraph AI API",
    description="Adaptive Learning Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(profile.router)
app.include_router(skill_graph_routes.router)
app.include_router(path_routes.router)
app.include_router(misc_routes.router)
app.include_router(demo_routes.router)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {"product": "SkillGraph AI", "tagline": "Don't just learn. Build your capability.", "docs": "/docs"}
