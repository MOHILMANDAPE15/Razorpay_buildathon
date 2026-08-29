"""FastAPI Application Entry Point for Aegis-RTO."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chatbot import router as chatbot_router
from app.api.lineage import router as lineage_router
from app.api.monitor import router as monitor_router
from app.api.playground import router as playground_router
from app.api.residual_mining import router as residual_mining_router
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
app.include_router(residual_mining_router, prefix="/api/v1")
app.include_router(scoring_router, prefix="/api/v1")
app.include_router(playground_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1")




@app.on_event("startup")
def startup_db_init():
    """Auto-initializes database schema and populates CSV order splits if empty."""
    try:
        from app.db.session import get_engine, Base
        from app.db.ingest import ingest_all_splits
        from sqlalchemy import text
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            try:
                count = conn.execute(text("SELECT COUNT(*) FROM orders_train")).scalar()
            except Exception:
                count = 0
            if not count or count == 0:
                print("[STARTUP] Ingesting canonical order datasets into database...")
                ingest_all_splits(engine=engine)
                print("[STARTUP] Ingestion complete.")
    except Exception as e:
        print(f"[STARTUP] DB init notice: {e}")


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
