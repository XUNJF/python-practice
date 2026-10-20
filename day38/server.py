"""
把笔记问答 Agent 做成网页

启动：
    python -m uvicorn server:app --reload
然后浏览器打开：
    http://127.0.0.1:8000
"""


from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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

