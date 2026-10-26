"""
多智能体版笔记助手（带步骤显示）

启动：
    python -m uvicorn server:app --reload
"""

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

import multi_agent

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


@app.get("/")
def index():
    return FileResponse("index.html")

def describe_step(node, update):
    if node == "supervisor":
        n = str(update.get("next",""))
        if "research" in n:
            return "🤔 主管：决定派研究员去查笔记"
        return "🤔 主管：决定派撰稿人去写"
    if node == "researcher":
        return "📚 研究员：笔记查完了"
    return f"...{node}"


@app.post("/chat/stream")
def chat_stream(req:ChatRequest):
    msg = req.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="消息不能为空")
    def gen():
        found_sources = []
        config = {"configurable":{"thread_id":req.thread_id}}
        for item in multi_agent.graph.stream(
            {"question":msg}, config=config, stream_mode=["updates","messages"]
        ):
            mode, data = item
            if mode == "updates":
                for node, update in data.items():
                    if node in ("writer","receive"):
                        continue
                    if node == "researcher":
                        found_sources[:] = update.get("sources",[])
                    yield json.dumps(
                        {"type":"step","text":describe_step(node, update)},
                        ensure_ascii=False,
                    ) + "\n"
            else:
                chunk, meta = data
                if meta.get("langgraph_node") == "writer" and chunk.content:
                    yield json.dumps(
                        {"type":"text","content":chunk.content},
                        ensure_ascii=False,
                    ) + "\n"
        yield json.dumps(
            {"type":"meta","sources":found_sources},ensure_ascii=False
        ) + "\n"
    return StreamingResponse(gen(), media_type="application/x-ndjson")
