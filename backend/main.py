from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyzer import analyze_web_content

app = FastAPI(title="WebRuler API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditRequest(BaseModel):
    url: str

@app.post("/api/audit")
async def audit_url(data: AuditRequest):
    if not data.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Trigger the Llama-powered accessibility analysis engine
    result = analyze_web_content(url=data.url)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)