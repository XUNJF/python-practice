"""
笔记问答 Agent（图 + 记忆 + 历史压缩）

给 server.py 用的：它只认 chat(问题, 会话id) 这一个函数。
"""

import json
import requests
import math
from typing import TypedDict, Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import RemoveMessage


with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()
with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()

model = ChatDeepSeek(model="deepseek-flash", api_key=ds_key, timeout=60, max_retries=3)


INDEX_FILE = "index.json"
TOP_K =5


def embed_batch(texts):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={"Authorization":f"Bearer {sf_key}","Content-Type":"application/json"},
        json={"model":"BAAI/bge-m3","input":texts},
        timeout=60,
    )
    d = response.json()
    if d.get("data") is None:
        raise RuntimeError(f"embedding 接口出错:{d}")
    vectors = [None] * len(texts)
    for item in d["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors

def cosine(a, b):
    dot = sum(a[i]*b[i] for i in range(len(a)))
    return dot / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b)))


def load_index():
    with open(INDEX_FILE,encoding="utf-8")as f:
        data = json.load(f)
    return data["chunks"], data["vectors"]

CHUNKS, VECTORS = load_index()


def search_notes(question):
    q_vec = embed_batch([question])[0]
    scores = sorted(
        ((cosine(q_vec, VECTORS[i]), i)for i in range(len(CHUNKS))),
        reverse=True,
    )
    hits = scores[:TOP_K]
    text = "".join(
        f"【来源：{CHUNKS[i]['source']}】\n{CHUNKS[i]['text']}\n\n"
        for _,i in hits
    )
    sources = []
    for _,i in hits:
        s = CHUNKS[i]['source']
        if s not in sources:
            sources.append(s)
    return text, sources

MAX_MESSAGES = 12
KEEP_RECENT = 6


class State(TypedDict):
    messages : Annotated[list, add_messages]
    question : str
    summary : str
    decision : str
    context : str
    sources : list
    answer : str


def compress(state):
    msgs = state["messages"]
    if len(msgs) <= MAX_MESSAGES:
        return {}
    old = msgs[:-KEEP_RECENT]
    原文 = "\n".join(
        f"{'用户' if m.type == 'human' else '助手'}:{m.content}" for m in old
    )
    已有 = state.get("summary","")
    提示 = (
        f"【已有摘要】\n{已有}\n\n【新的对话】\n{原文}\n\n"
        if 已有 else f"【对话】\n{原文}\n\n"
    )
    reply = model.invoke([
        {"role":"system","content":
        "把下面这段对话压缩成一段简短摘要。\n"
        "只保留：用户问了什么、结论是什么、有哪几个关键概念。\n"
        "不要评论，不要分段，200 字以内。"},
        {"role":"user","content":提示},
    ])
    return {
        "summary":reply.content.strip(),
        "messages":[RemoveMessage(id = m.id)for m in old],
    }


def decide(state):
    rules = (
        "判断用户的问题需不需要查他的学习笔记。\n"
        "回答只能用下面两个词之一，不要标点、不要解释：\n"
        "  search —— 当问题是【知识点、概念、技术、怎么用】这类\n"
        "  chat   —— 当问题是【打招呼、闲聊、算数、别的杂事】\n"
    )
    reply = model.invoke([
        {"role":"system","content":rules},
        {"role":"user","content":state['question']},
    ])
    return {
        "decision":reply.content.strip().lower(),
        "messages":[{"role":"user","content":state['question']}],
    }


def route(state):
    return "need_search" if "search" in state["decision"] else "no_search"

def retrieve(state):
    text , sources = search_notes(state['question'])
    return {"context":text,"sources":sources}


def 拼历史(state):
    out = []
    if state.get("summary"):
        out.append({"role":"system","content":f"【之前聊过的内容摘要】\n{state['summary']}"})
    out += list(state["messages"])
    return out

def answer_with_notes(state):
    rules = (
        "你是一个学习助手。只根据提供的【资料】回答。\n"
        "资料里没有就直说「笔记里没有提到」。回答时注明来源。"
    )
    reply = model.invoke(
        [{"role":"system","content":rules}]
        + 拼历史(state)
        + [{"role":"user","content":f"【资料】\n{state['context']}"}]
    )
    return {
        "answer":reply.content,
        "messages":[{"role":"assistant","content":reply.content}]}


def answer_directly(state):
    reply = model.invoke(
        [{"role":"system","content":"你是一个学习助手，回答简短点。"}]
        + 拼历史(state)
    )
    return {
        "answer":reply.content,
        "messages":[{"role":"assistant","content":reply.content}]
    }

builder = StateGraph(State)
builder.add_node("compress",compress)
builder.add_node("decide",decide)
builder.add_node("retrieve",retrieve)
builder.add_node("answer_with_notes",answer_with_notes)
builder.add_node("answer_directly",answer_directly)

builder.add_edge(START,"compress")
builder.add_edge("compress","decide")
builder.add_conditional_edges("decide",route,{"need_search":"retrieve","no_search":"answer_directly"})
builder.add_edge("retrieve","answer_with_notes")
builder.add_edge("answer_with_notes",END)
builder.add_edge("answer_directly",END)

graph = builder.compile(checkpointer=InMemorySaver())

def chat(question, thread_id = "default"):
    config = {"configurable":{"thread_id":thread_id}}
    out = graph.invoke({"question":question},config=config)
    return {
        "answer":out["answer"],
        "sources":out.get("sources",[]),
        "used_notes":out.get("decision","").startswith("search"),
    }