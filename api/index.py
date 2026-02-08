from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from core.agent_graph import app as agent_app

from core.database import engine, Base
from contextlib import asynccontextmanager

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    # Commented out for Vercel: Database is pre-seeded and filesystem might be read-only
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: close connection
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
# app.mount("/static", StaticFiles(directory="static"), name="static") # Optional if we add local assets

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that streams the agent's response.
    """
    print(f"DEBUG: Processing chat request: {request.message}")
    try:
        inputs = {"messages": [HumanMessage(content=request.message)]}
        # Config for thread_id if needed in the future for persistence
        config = {"configurable": {"thread_id": request.thread_id}} if request.thread_id else {}

        # Generator for streaming response
        async def event_generator():
            print("DEBUG: Starting event generator")
            try:
                # Stream events from the graph
                async for event in agent_app.astream(inputs, config=config):
                    print(f"DEBUG: Event received: {event.keys()}")
                    for key, value in event.items():
                        # We can categorize events. 
                        # If it's from 'agent', it usually contains the AIMessage.
                        if key == "agent":
                            # This node returns "messages": [response]
                            messages = value.get("messages", [])
                            if messages:
                                last_msg = messages[-1]
                                content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                                print(f"DEBUG: Yielding content length: {len(content)}")
                                yield json.dumps({"type": "agent", "content": content}) + "\n"
                        elif key == "tools":
                            # Tool outputs
                            print("DEBUG: Tool executed")
                            messages = value.get("messages", [])
                            if messages and isinstance(messages[-1], ToolMessage):
                                 yield json.dumps({"type": "tool", "content": "Executing tool..."}) + "\n"
            except Exception as stream_err:
                print(f"CRITICAL STREAM ERROR: {stream_err}")
                import traceback
                traceback.print_exc()
                yield json.dumps({"type": "agent", "content": f"**System Error**: {str(stream_err)}"}) + "\n"

        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    except Exception as e:
        print(f"CRITICAL ENDPOINT ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/debug")
async def debug_endpoint():
    import os
    import sys
    
    # Check DB File
    db_path = "pharma_agent.db"
    db_exists = os.path.exists(db_path)
    db_size = os.path.getsize(db_path) / (1024*1024) if db_exists else 0
    
    # Check API Key
    api_key = settings.OPENROUTER_API_KEY
    has_key = bool(api_key and api_key.startswith("sk-or"))
    
    return {
        "status": "debug",
        "cwd": os.getcwd(),
        "files_in_root": os.listdir("."),
        "db_exists": db_exists,
        "db_size_mb": db_size,
        "has_api_key": has_key,
        "python_version": sys.version,
        "env_vars": {k: v for k, v in os.environ.items() if k.startswith("VERCEL") or k in ["OLLAMA_BASE_URL", "DATABASE_URL"]}
    }
