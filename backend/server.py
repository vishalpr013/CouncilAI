from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph.builder import graph
from app.tools.financials import calculate_dcf
import uvicorn
import json

app = FastAPI(title="CouncilAI API", description="FastAPI Backend for CouncilAI Agent Workflow")

# Enable CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your React domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    ticker: str
    raw_financials: dict
    dcf_valuation: dict
    news_summary: list
    research: str
    analysis: str
    critique: str
    final_answer: str

class RecalculateRequest(BaseModel):
    ticker: str
    revenue_growth: float
    discount_rate: float
    terminal_multiple: float
    margin_of_safety: float

@app.get("/")
async def root():
    return {"status": "online", "message": "CouncilAI Backend Service"}

@app.post("/api/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        # Run graph synchronously
        result = graph.invoke({"question": request.question})
        return QueryResponse(
            question=request.question,
            ticker=result.get("ticker", "NONE"),
            raw_financials=result.get("raw_financials", {}),
            dcf_valuation=result.get("dcf_valuation", {}),
            news_summary=result.get("news_summary", []),
            research=result.get("research", ""),
            analysis=result.get("analysis", ""),
            critique=result.get("critique", ""),
            final_answer=result.get("final_answer", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dcf-recalculate")
async def recalculate_valuation(request: RecalculateRequest):
    try:
        result = calculate_dcf(
            ticker=request.ticker,
            revenue_growth=request.revenue_growth,
            discount_rate=request.discount_rate,
            terminal_multiple=request.terminal_multiple,
            margin_of_safety=request.margin_of_safety
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Wait for query question from frontend
            data = await websocket.receive_text()
            payload = json.loads(data)
            question = payload.get("question")
            
            if not question:
                await websocket.send_text(json.dumps({"error": "Empty question"}))
                continue

            # Stream LangGraph state updates
            # Use compiled graph streaming
            await websocket.send_text(json.dumps({"type": "status", "node": "system", "message": "Initializing Investment Committee..."}))
            
            # Start streaming LangGraph events
            state = {"question": question}
            
            # We stream the graph asynchronously to prevent blocking the event loop
            async for event in graph.astream(state, stream_mode="updates"):
                for node_name, node_output in event.items():
                    # Send node-specific update details
                    # Filter details to prevent sending huge payloads
                    safe_output = {}
                    for k, v in node_output.items():
                        # Exclude raw lists or dicts from large textual state logs if needed, 
                        # but send what the frontend needs
                        if k in ["research", "analysis", "critique", "final_answer", "ticker", "dcf_valuation", "raw_financials", "news_summary"]:
                            safe_output[k] = v

                    await websocket.send_text(json.dumps({
                        "type": "node_update",
                        "node": node_name,
                        "status": "completed",
                        "output": safe_output
                    }))
            
            await websocket.send_text(json.dumps({"type": "complete", "message": "Report generation finished."}))
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except:
            pass

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
