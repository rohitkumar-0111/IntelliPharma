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
    try:
        inputs = {"messages": [HumanMessage(content=request.message)]}
        # Config for thread_id if needed in the future for persistence
        config = {"configurable": {"thread_id": request.thread_id}} if request.thread_id else {}

        # Generator for streaming response
        async def event_generator():
            # Stream events from the graph
            # We use astream_events or astream depending on what we want to send back.
            # Here we want to stream the final answer tokens if possible, or intermediate steps.
            # Using astream gives updates on state keys.
            
            # Simple streaming of the final LLM response is tricky with LangGraph unless we use a callback or specific streaming mode.
            # For this Phase, let's stream the final message content chunk by chunk if LangGraph supports it, 
            # OR just stream the node updates. 
            
            # Better approach for Vercel timeout prevention: Stream intermediate steps.
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
                            # Send the full content as a chunk (or we could try token streaming if we bind streaming=True to LLM)
                            # To properly stream tokens, we'd need to use .astream_events() which is more granular.
                            # For now, let's send node outputs.
                            yield json.dumps({"type": "agent", "content": content}) + "\n"
                    elif key == "tools":
                        # Tool outputs
                        messages = value.get("messages", [])
                        if messages and isinstance(messages[-1], ToolMessage):
                             yield json.dumps({"type": "tool", "content": "Executing tool..."}) + "\n"
                             # Optionally send the tool result if needed, but usually user just wants the final answer.

        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
