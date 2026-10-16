"""
把 RAG 接进图里

判断要不要查笔记 → 要就检索再回答，不要就直接聊
"""


import json
import math
import requests
from typing import TypedDict

from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END


with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()

with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()


model = ChatDeepSeek(model="deepseek-flash",api_key=ds_key,timeout=60,max_retries=3)


INDEX_FILE = "index.json"
TOP_K = 5


def embed_batch(texts):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sf_key}",
            "Content-Type":"application\json",
        },
        json={"model":"BAAI/bge-m3","input":texts},
        timeout=60,
    )
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors

def cosine(a,b):
    dot = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
    la = 0
    for x in a:
        la += x * x
    lb = 0
    for x in b:
        lb += x * x
    return dot / (math.sqrt(la) * math.sqrt(lb))


def load_index():
    with open(INDEX_FILE,encoding="utf-8")as f:
        data = json.load(f)
        return data["chunks"], data["vectors"]

CHUNKS, VECTORS = load_index()
print(f"[载入索引] {len(CHUNKS)} 块笔记")


def search_notes(question):
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(CHUNKS)):
        scores.append((cosine(q_vec,VECTORS[i]),i))
    scores.sort(reverse=True)
    text = ""
    for score, i in scores[:TOP_K]:
        c = CHUNKS[i]
        text += f"【来源：{c['source']}】\n{c['text']}\n\n"
    return text

class State(TypedDict):
    question:str
    decision:str
    context:str
    answer:str


def decide(state):
    print("  [decide] 判断要不要查笔记")
    rules = (
        "判断用户的问题需不需要查他的学习笔记。\n"
        "需要查：问某个知识点、概念、技术怎么用\n"
        "（比如 RAG、BM25、函数、异常处理、FastAPI、embedding）\n"
        "不需要查：打招呼、闲聊、数学计算、别的杂事\n\n"
        "只回一个词：search 或 chat\n"
        "不要标点，不要解释。"
    )
    reply = model.invoke([
        {"role":"system","content":rules},
        {"role":"user","content":state["question"]},
    ])
    decision = reply.content.strip().lower()
    print(f"             -> {decision!r}")
    return {"decision":decision}

def route(state):
    if "search" in state["decision"]:
        return "need_search"
    return "no_search"

def retrieve(state):
    print("  [retrieve] 检索笔记")
    return {"context":search_notes(state["question"])}

def answer_with_notes(state):
    print("  [answer] 根据笔记回答")
    rules = (
        "你是一个学习助手，帮用户回忆他学过的内容。\n"
        "只根据下面提供的【资料】回答。\n"
        "资料里没有相关信息，就直说「笔记里没有提到」。\n"
        "回答时注明是哪份笔记（资料里写了来源）。"
    )
    user_msg = f"【资料】\n{state['context']}\n【问题】\n{state['question']}"
    reply = model.invoke([
        {"role":"system","content":rules},
        {"role":"user","content":user_msg},
    ])
    return {"answer":reply.content}

def answer_directly(state):
    print("  [chat] 直接回答")
    reply = model.invoke([
        {"role":"system","content":"你是一个学习助手，回答简短点。"},
        {"role":"user","content":state['question']},
    ])
    return {"answer":reply.content}


builder = StateGraph(State)

builder.add_node("decide",decide)
builder.add_node("retrieve",retrieve)
builder.add_node("answer_with_notes",answer_with_notes)
builder.add_node("answer_directly",answer_directly)

builder.add_edge(START, "decide")

builder.add_conditional_edges(
    "decide",
    route,
    {
        "need_search":"retrieve",
        "no_search":"answer_directly",
    },
)

builder.add_edge("retrieve","answer_with_notes")
builder.add_edge("answer_with_notes",END)
builder.add_edge("answer_directly",END)

graph = builder.compile()

for q in ["你好呀，你是谁", "RAG 是什么？", "帮我算一下 3 的平方"]:
    print()
    print("="*62)
    print(f"问：{q}")
    print("="*62)
    out = graph.invoke({"question":q})
    print()
    print(out["answer"][:300])