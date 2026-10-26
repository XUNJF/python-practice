import asyncio
import time
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_deepseek import ChatDeepSeek

key = open("key.txt",encoding="utf-8").read().strip()
model = ChatDeepSeek(model="deepseek-flash", api_key=key, timeout=60, max_retries=3)


class State(TypedDict):
    messages: Annotated[list, add_messages]

def answer(state):
    r = model.invoke(
        [
            {"role":"system","content":"用一段话解释，100字左右"},
            {"role":"user","content":state["messages"][-1].content}
        ]
    )
    return {"messsages":[{"role":"assistant","content":r.content}]}

builder = StateGraph(State)
builder.add_node("answer",answer)
builder.add_edge(START, "answer")
builder.add_edge("answer", END)
graph = builder.compile()


print("=" * 60)
print("  1. 普通 invoke —— 等全部出来")
print("=" * 60)
start = time.time()
out = graph.invoke({"messages":[{"role":"user","content":"RAG 是什么"}]})
print(out["messages"][-1].content[:150])
print(f"\n总共用了：{time.time()-start:.2f}秒")
print("★ 这 3 秒里，屏幕上什么都没有")


print()
print("=" * 60)
print("  2. 流式 stream —— 一个字一个字冒")
print("=" * 60)
strat = time.time()
first = None
for chunk, meta in graph.stream(
    {"messages":[{"role":"user","content":"RAG 是什么"}]},
    stream_mode="messages",
):
    if first is None:
        first = time.time() - start
    if chunk.content:
        print(chunk.content, end="", flush=True)

print()
print(f"\n总共用了：{time.time()-start:.2f}秒")
print(f"首字出现：{first:.2f}秒   ← 关键数字")