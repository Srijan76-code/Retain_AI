from fastapi import FastAPI, Body
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

from app.graph.builder import build_retention_graph
from typing import Dict, Any

app = FastAPI(title="Retain AI Backend")

# Initialize the graph once at startup
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
    """
    Trigger the Retention Analysis Graph.
    Expected items in body: 'raw_csv_path' (string) and 'questionnaire' (dict).
    """
    # 1. Prepare the initial state for the LangGraph
    initial_state = {
        "raw_csv_path": req_body.get("raw_csv_path", ""),
        "questionnaire": req_body.get("questionnaire", {}),
        "iteration_count": 0,
        "errors": []
    }

    # 2. Execute the graph (invoke runs it to completion synchronously)
    final_state = graph.invoke(initial_state)

    # 3. Return the cumulative state result
    return {
        "status": "success",
        "result": final_state
    }