"""
给 RAG 图加记忆：让它能连着聊

两个关键：
    ① 状态里加 messages 字段，用 add_messages 让它【累积】
    ② 节点把历史交给模型，而不只是当前这一句
"""

import json
import math
import requests
from typing import TypedDict, Annotated

from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import InMemorySaver


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
        headers={"Authorization":f"Bearer {sf_key}","Content-Type":"application/json"},
        json={"model":"BAAI/bge-m3","input":texts},
        timeout=60,
    )
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors

def cosine(a, b):
    dot = sum(a[i]*b[i] for i in range(len(a)))
    return dot/(math.sqrt(sum(x*x for x in a)))*math.sqrt(sum(x*x for x in b))


def load_index():
    with open(INDEX_FILE,encoding="utf-8")as f:
        data = json.load(f)
    return data["chunks"], data["vectors"]

CHUNKS, VECTORS = load_index()
print(f"[载入索引] {len(CHUNKS)} 块笔记")

def search_notes(question):
    q_vec = embed_batch([question])[0]
    scores = sorted(
        ((cosine(q_vec,VECTORS[i]),i) for i in range(len(CHUNKS))),
        reverse=True,
    )
    return "".join(
        f"【来源:{CHUNKS[i]['source']}】\n{CHUNKS[i]['text']}\n\n"
        for _, i in scores[:TOP_K]
    )


class State(TypedDict):
    messages:Annotated[list, add_messages]
    question:str
    decision:str
    context:str
    answer:str


def decide(state):
    print("  [decide]")
    rules = (
    "你要判断用户的问题要不要查他的学习笔记。\n"
    "回答只能用下面两个词之一，不要标点、不要解释：\n"
    "  search —— 当问题是【知识点、概念、技术、怎么用】这类\n"
    "  chat   —— 当问题是【打招呼、闲聊、算数、别的杂事】\n"
    )
    reply = model.invoke([
        {"role":"system","content":rules},
        {"role":"user","content":state['question']},
    ])
    d =reply.content.strip().lower()
    print(f"             -> {d!r}")
    return {
        "decision":d,
        "messages":[{"role":"user","content":state["question"]}],
    }


def route(state):
    return "need_search" if "search" in state["decision"] else "no_search"

def retrieve(state):
    print("  [retrieve]")
    return {"context":search_notes(state["question"])}

def answer_with_notes(state):
    print("  [answer]")
    rules = (
        "你是一个学习助手。只根据提供的【资料】回答。\n"
        "资料里没有就直说「笔记里没有提到」。回答时注明来源。"
    )
    reply = model.invoke(
        [{"role":"system","content":rules}]
        + list(state["messages"])
        + [{"role":"user","content":f"【资料】\n{state['context']}"}]
    )
    return {
        "answer":reply.content,
        "messages":[{"role":"assistant","content":reply.content}]
    }

def answer_directly(state):
    print("  [chat]")
    reply = model.invoke(
        [{"role":"system","content":"你是一个学习助手，回答简短点。"}]
        + list(state["messages"])
    )
    return {
        "answer":reply.content,
        "messages":[{"role":"assistant","content":reply.content}]
    }



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

builder.add_edge("retrieve", "answer_with_notes")
builder.add_edge("answer_with_notes", END)
builder.add_edge("answer_directly", END)


graph = builder.compile(checkpointer=InMemorySaver())


config = {"configurable":{"thread_id":"chat-1"}}


for q in ["RAG 是什么？", "我刚才问的是什么？", "那它有什么缺点？"]:
    print()
    print("=" * 60)
    print(f"问：{q}")
    print("=" * 60)
    out = graph.invoke({"question":q},config=config)
    print(f"  历史条数：{len(out['messages'])}")
    print()
    print(out["answer"][:200])