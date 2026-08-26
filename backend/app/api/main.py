"""FastAPI Application Entry Point for Aegis-RTO."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.lineage import router as lineage_router
from app.api.monitor import router as monitor_router
from app.api.scoring import scoring_router
from app.db.session import check_db_connection

app = FastAPI(
    title="Aegis-RTO API",
    description="Self-Evolving RTO & COD Fraud Detection Engine REST API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lineage_router, prefix="/api/v1")
app.include_router(monitor_router, prefix="/api/v1")
app.include_router(scoring_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["System Health"])
def health_check():
    """Service health check and database connectivity probe."""
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database_connected": db_ok,
        "service": "Aegis-RTO",
        "version": "1.0.0",
    }
