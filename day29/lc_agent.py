import json
import math
import requests

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek



with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()
with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()

with open("index.json",encoding="utf-8")as f:
    _data = json.load(f)

CHUNKS =_data["chunks"]
VECTORS = _data["vectors"]


def embed(text):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sf_key}",
            "Content-Type":"application/json",
        },
        json={"model":"BAAI/bge-m3","input":text},
        timeout=60,
    )
    return response.json()["data"][0]["embedding"]


def cosine(a, b):
    dot = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
    len_a = 0
    for x in a:
        len_a += x * x
    len_b = 0
    for x in b:
        len_b += x * x
    return dot/(math.sqrt(len_b)*math.sqrt(len_a))



@tool
def search_notes(question: str) -> str:
    """在用户的学习笔记里检索，返回最相关的片段。
    当用户问到他笔记里学过的知识点时使用（比如 RAG、BM25、
    函数、异常处理、FastAPI 等）。闲聊时不要调用。"""
    q_vec = embed(question)
    scores = []
    for i in range(len(CHUNKS)):
        scores.append((cosine(q_vec, VECTORS[i]), i))
    scores.sort(reverse=True)
    text = ""
    for score, i in scores[:5]:
        c = CHUNKS[i]
        text += f"【来源：{c['source']}】\n{c['text']}\n\n"
    return text

@tool
def calculate(a:float, b:float, operation:str)->float:
    """做四则运算。当用户需要算数时使用。
    operation 只能是 + - * / 之一。"""
    if operation == "+":
        return a + b
    if operation == "-":
        return a - b
    if operation == "/":
        return a / b
    if operation == "*":
        return a * b
    return 0

@tool
def get_time()->str:
    """查询当前的日期和时间。当用户问现在几点、今天几号时使用。"""
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

model = ChatDeepSeek(model="deepseek-flash",api_key=ds_key)

agent = create_agent(
    model,
    tools = [search_notes, get_time, calculate],
    system_prompt = "你是一个学习助手，需要外部信息时调用工具。",
)

for q in ["RAG 是什么", "帮我算 1738 × 2947", "你好呀"]:
    print("="*60)
    print(f"问：{q}")
    print("="*60)
    result = agent.invoke({"messages":[{"role":"user","content":q}]})
    used = []
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                used.append(tc["name"])
    print(f"  用了：{used if used else '（没用工具）'}")
    print()
    print(result["messages"][-1].content)
    print()