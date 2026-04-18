from fastapi import FastAPI, Body, HTTPException
from dotenv import load_dotenv
import uuid
import traceback

load_dotenv()

from app.graph.builder import build_retention_graph
from typing import Dict, Any

app = FastAPI(title="Retain AI Backend")

graph = build_retention_graph()

@app.get("/")
async def root():
    return {"message": "Retain AI Backend running"}

@app.post("/analyze")
async def run_analysis(
    req_body: Dict[str, Any] = Body(
        ...,
        example={
            "raw_csv_path": "data/sample.csv",
            "questionnaire": {"industry": "SaaS", "size": "100-500"}
        }
    )
):
    initial_state = {
        "raw_csv_path": req_body.get("raw_csv_path", ""),
        "questionnaire": req_body.get("questionnaire", {}),
        "iteration_count": 0,
        "discovery_attempts": 0,
        "retry_count": 0,
        "errors": [],
    }

    try:
        final_state = graph.invoke(initial_state)
        return {"status": "success", "result": final_state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) + "\n" + traceback.format_exc())
