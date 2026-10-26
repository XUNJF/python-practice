from typing import TypedDict,Annotated

from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph,START,END,add_messages

from rag_agent import search_notes, _read_key
import os
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


ds_key = _read_key("DEEPSEEK_API_KEY","key.txt")
model = ChatDeepSeek(model="deepseek-flash", api_key=ds_key, timeout=60, max_retries=3)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    notes: str
    answer: str
    next: str
    sources: list

SUPERVISOR_PROMPT = """你是主管，手下有两个专员：
- 研究员：负责翻他的学习笔记，找原始资料
- 撰稿人：负责根据资料写答案

看当前进度，决定下一步派谁。
只回一个词：research 或 write

什么时候派研究员：问题跟他的学习内容有关，而且还没查过资料
什么时候派撰稿人：资料已经查到了，或者这个问题根本不用查资料（比如闲聊）"""

def receive(state):
    return {
        "messages":[{"role":"user","content":state["question"]}],
        "notes":"",
        "answer":"",
        "sources":[],
        "next":"",
    }

def supervisor(state):
    history = state.get("messages",[])[-6:]
    status = (f"当前进度：资料={'有' if state.get('notes') else '没有'},"
              f"答案={'有' if state.get('answer') else '没有'}")
    msgs = [{"role":"system","content":SUPERVISOR_PROMPT}]
    msgs.extend(history)
    msgs.append({"role":"user","content":status})
    r = model.invoke(msgs)
    return {"next":r.content.strip().lower()}
    

def researcher(state):
    text, sources = search_notes(state['question'])
    return {"notes":text, "sources":sources}

def writer(state):
    notes = state.get("notes") or ""
    if notes:
        system = ("只根据下面提供的【资料】回答；资料里没有就说「资料里没有提到这个」。\n\n"
                  f"【资料】\n{notes}")
    else:
        system = "根据前面的对话自然回应；闲聊就简短回应。"
    msgs = [{"role":"system","content":system}]
    msgs.extend(state.get("messages",[]))
    r = model.invoke(msgs)
    return {
        "answer":r.content,
        "messages":[{"role":"assistant","content":r.content}],
    }

def route(state):
    n = state.get("next","")
    if "research" in n:
        return "researcher"
    return "writer"

builder = StateGraph(State)
builder.add_node("receive",receive)  
builder.add_node("supervisor",supervisor)
builder.add_node("researcher",researcher)
builder.add_node("writer",writer)

builder.add_edge(START,"receive")            # ← START 先到 receive
builder.add_edge("receive","supervisor") 
builder.add_conditional_edges(
    "supervisor",
    route,
    {
        "researcher":"researcher",
        "writer":"writer",
    }
)

builder.add_edge("researcher","supervisor")
builder.add_edge("writer",END)

os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/记忆.db", check_same_thread=False)
graph = builder.compile(checkpointer=SqliteSaver(conn))


if __name__ == "__main__":
    cfg = {"configurable": {"thread_id": "test"}}

    for q in ["我是小明", "我是谁？", "RAG 是什么？"]:
        print("=" * 60)
        print(f"  问题：{q}")
        print("=" * 60)
        out = graph.invoke({"question": q}, config=cfg)
        print(f"  主管决定：{out.get('next')}")
        print(f"  查过资料：{'是' if out.get('notes') else '否'}")
        print(f"  答案：{out.get('answer', '')[:100]}")
        print()