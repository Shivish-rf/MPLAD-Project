from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.pipeline.pipeline import run_pipeline

app = FastAPI(
    title="MPLADS AI Risk Detection API",
    description=(
        "AI-powered system for detecting anomalies, "
        "fraud patterns, compliance issues and "
        "inefficiencies in MPLADS works."
    ),
    version="1.0.0",
)

# 1. Enable CORS for frontend dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain/port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
  return {
      "message": "MPLADS AI Risk Detection API is running",
      "status": "online",
  }


@app.get("/health")
def health():
  return {"status": "healthy"}


@app.get("/analyze/{work_id:path}")
def analyze_work(work_id: str):
  try:
    result = run_pipeline(work_id)

    # If the database query inside run_pipeline returned None
    if not result:
      raise HTTPException(
          status_code=404,
          detail=f"Work ID '{work_id}' not found in the database.",
      )

    return {
      "success": True,
      "work_id": result["work_id"],
      "quick_filter": result.get("quick_filter"),
      "engines": {
          "duplicate_pattern": result.get("duplicate_engine"),
          "anomaly": result.get("anomaly_engine"),
          "compliance": result.get("compliance_engine"),
          "delay_progress": result.get("delay_progress_engine"),
      },
      "final_risk": result.get("final_risk"),
      "risk_reasons": result.get("risk_reasons", []),
  }

  except HTTPException:
    # Re-raise explicit 404s without turning them into 500s
    raise
  except Exception as e:
    # Log unexpected ML pipeline or database crashes
    raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")