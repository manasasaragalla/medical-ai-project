from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import interaction

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HCP CRM API",
    description="AI-First CRM for Healthcare Professional Interaction Logging",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interaction.router, prefix="/api/interactions", tags=["Interactions"])

@app.get("/")
def root():
    return {"message": "HCP CRM API is running"}