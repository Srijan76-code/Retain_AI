from fastapi import FastAPI, Body, HTTPException
from dotenv import load_dotenv
import uuid
import traceback
import inngest
import inngest.fast_api
# import logging
load_dotenv()

from app.graph.builder import build_retention_graph
from typing import Dict, Any

app = FastAPI(title="Retain AI Backend")

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
async def analyze_retention_job(ctx: inngest.Context):
    event_data = ctx.event.data
    step = ctx.step
    
    initial_state = {
        "raw_csv_path": event_data.get("raw_csv_path", ""),
        "questionnaire": event_data.get("questionnaire", {}),
        "iteration_count": 0,
        "discovery_attempts": 0,
        "retry_count": 0,
        "errors": [],
    }

    # Define a synchronous runner for the graph
    def execute_graph():
        return graph.invoke(initial_state)

    try:
        # Run graph invocation within an inngest step
        final_state = await step.run("execute_langgraph", execute_graph)
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
        # Send event to Inngest to trigger the background job
        await inngest_client.send(
            inngest.Event(
                name="app/analyze",
                data=req_body
            )
        )
        return {"status": "queued", "message": "Analysis started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) + "\n" + traceback.format_exc())

inngest.fast_api.serve(app, inngest_client, [analyze_retention_job])