from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.content import router as content_router
from app.api.edit import router as edit_router
from app.api.linkedin import router as linkedin_router
from app.config.database import Base, engine

# Create tables if they don't exist (simplifying for now instead of alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Social Media Content Creation Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(content_router, prefix="/api/content", tags=["Content"])
app.include_router(edit_router, prefix="/api/content", tags=["Edit"])
app.include_router(linkedin_router, prefix="/api/linkedin", tags=["LinkedIn"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Social Media Content Creation Backend"}
