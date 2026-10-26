"""
把笔记问答 Agent 做成网页（支持流式输出）

启动：
    python -m uvicorn server:app --reload
然后浏览器打开：
    http://127.0.0.1:8000
"""


import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse,StreamingResponse
from pydantic import BaseModel


import rag_agent

app =FastAPI()


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/chat")
def chat(req:ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    return rag_agent.chat(req.message.strip(), req.thread_id)


@app.post("/chat/stream")
def chat_stream(req:ChatRequest):
    msg = req.message.strip()
    if not msg:
        raise HTTPException(status_code=400,detail="消息不能为空")
    def gen():
        config = {"configurable":{"thread_id":req.thread_id}}
        for chunk, meta in rag_agent.graph.stream(
            {"question":msg},config=config,stream_mode="messages"
        ):
            node = meta.get("langgraph_node")
            if node in ("answer_with_notes","answer_directly") and chunk.content:
                yield json.dumps(
                    {"type":"text","content":chunk.content}, ensure_ascii=False
                ) + "\n"

        state = rag_agent.graph.get_state(config).values
        yield json.dumps({
            "type":"meta",
            "sources":state.get("sources",[]),
            "used_notes":state.get("decision","").startswith("search"),
        },ensure_ascii=False) + "\n"

    return StreamingResponse(gen(),media_type = "application/x-ndjson")