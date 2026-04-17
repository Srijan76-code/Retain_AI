from fastapi import FastAPI

app = FastAPI(title="Your Backend")

@app.get("/")
async def root():
    return {"message": "Backend running"}