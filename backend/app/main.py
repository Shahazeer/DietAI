from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.mongodb import mongodb
from app.routes import patients, reports, diet

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    yield
    await mongodb.disconnect()

app = FastAPI(
    title="Dietician Agent API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router, prefix="/api/patients" , tags=["Patients"])
app.include_router(reports.router, prefix="/api/reports" , tags=["Lab Reports"])
app.include_router(diet.router, prefix="/api/diet" , tags=["Diet Plans"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}