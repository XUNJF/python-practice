"""
把 Agent 包成一个 HTTP 服务

启动：python -m uvicorn server:app --reload
然后浏览器打开 http://127.0.0.1:8000
"""


from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import agent

app = FastAPI()

class ASKRequest(BaseModel):
    goal : str




@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/run")
def run(req:ASKRequest):
    if not req.goal.strip():
        raise HTTPException(status_code=400,detail="目标不能为空")
    answer, steps = agent.run_agent(req.goal)
    return {"answer":answer, "steps":steps}

