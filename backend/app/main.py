from fastapi import FastAPI, Body, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uuid
import traceback
import inngest
import inngest.fast_api
import asyncio
import json
# import logging
load_dotenv()

from app.graph.builder import build_retention_graph
from typing import Dict, Any

app = FastAPI(title="Retain AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_streams: Dict[str, asyncio.Queue] = {}

# Create an Inngest client
inngest_client = inngest.Inngest(
    app_id="fast_api_example",
#     logger=logging.getLogger("uvicorn"),
)

@inngest_client.create_function(
    fn_id="analyze_retention_job",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="app/analyze"),
)
async def analyze_retention_job(ctx: inngest.Context, step: inngest.Step):
    event_data = ctx.event.data
    
    initial_state = {
        "raw_csv_path": event_data.get("raw_csv_path", ""),
        "questionnaire": event_data.get("questionnaire", {}),
        "iteration_count": 0,
        "discovery_attempts": 0,
        "retry_count": 0,
        "errors": [],
    }

    job_id = event_data.get("job_id")

    # Define an async runner for the graph to stream updates internally
    async def execute_and_stream():
        queue = active_streams.get(job_id) if job_id else None
        final_state = None
        
        async for state in graph.astream(initial_state, stream_mode="values"):
            final_state = state
            if not queue:
                continue
                
            node = state.get("current_node")
            
            if node == "feature_engineering":
                fs = state.get("feature_store", {})
                risk = fs.get("predictive_churn_risk", {})
                has_model = "high_risk_customers_count" in risk and "error" not in risk

                high_risk = risk.get("high_risk_customers_count", 0)
                total = risk.get("total_active_evaluated", 0)
                pct = risk.get("risk_segment_pct", 0)

                if has_model:
                    if pct > 0.3:
                        insight = f"{high_risk} users ({round(pct*100)}%) show high churn probability in the near term"
                    elif pct > 0.1:
                        insight = f"A focused segment of {high_risk} users is driving most immediate churn risk"
                    elif high_risk > 0:
                        insight = f"{high_risk} users identified with significantly shorter expected lifetime"
                    else:
                        insight = "No immediate high-risk patterns detected — monitoring recommended"
                else:
                    insight = "Risk model could not be trained — ensure your dataset has churn and tenure columns"

                await queue.put({
                    "type": "risk_ready",
                    "message": "Risk analysis complete.",
                    "data": {
                        "high_risk_count": high_risk,
                        "total_active": total,
                        "risk_pct": round(pct * 100, 1),
                        "confidence": round(risk.get("concordance_index", 0) * 100) if has_model else 0,
                        "insight": insight,
                        "has_model": has_model,
                    }
                })

            elif node == "behavioral_map":
                await queue.put({
                    "type": "churn_profile_ready",
                    "message": "Churn profile and behavior mapping complete.",
                    "data": {
                        "behavior_cohorts": state.get("behavior_cohorts", []),
                        "behavior_curves": state.get("behavior_curves", {}),
                    }
                })

            elif node == "diagnosis_merge":
                diagnosis = state.get("diagnosis_results", {})
                await queue.put({
                    "type": "diagnosis_ready",
                    "message": "Core problems diagnosed.",
                    "data": {
                        "merged_hypotheses": diagnosis.get("merged_hypotheses", []),
                    }
                })

            elif node == "execution_architect":
                await queue.put({
                    "type": "solution_ready",
                    "message": "Final playbook generated.",
                    "data": {
                        "final_playbook": state.get("final_playbook"),
                    }
                })
                
        if queue:
            await queue.put({"type": "complete", "message": "Analysis finished.", "data": {}})
            
        return final_state

    try:
        # Run async stream invocation within an inngest step
        final_state = await step.run("execute_langgraph", execute_and_stream)
        return {"status": "success", "result": final_state}
    except Exception as e:
        ctx.logger.error(f"Error in background job: {str(e)}\n{traceback.format_exc()}")
        raise e


graph = build_retention_graph()

@app.get("/")
async def root():
    return {"message": "Retain AI Backend running"}

@app.post("/analyze")
async def run_analysis(
    req_body: Dict[str, Any] = Body(
        ...,
        examples=[{
            "raw_csv_path": "data/sample.csv",
            "questionnaire": {"industry": "SaaS", "size": "100-500"}
        }]
    )
):
    try:
        job_id = str(uuid.uuid4())
        active_streams[job_id] = asyncio.Queue()
        req_body["job_id"] = job_id
        
        # Send event to Inngest to trigger the background job
        await inngest_client.send(
            inngest.Event(
                name="app/analyze",
                data=req_body
            )
        )
        return {"status": "queued", "job_id": job_id, "message": "Analysis started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) + "\n" + traceback.format_exc())

@app.get("/analyze/stream/{job_id}")
async def stream_job(job_id: str, request: Request):
    if job_id not in active_streams:
        raise HTTPException(status_code=404, detail="Job not found or already completed")
        
    queue = active_streams[job_id]

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                yield f"data: {json.dumps(event)}\n\n"
                
                if event["type"] == "complete":
                    break
        finally:
            active_streams.pop(job_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

inngest.fast_api.serve(app, inngest_client, [analyze_retention_job])