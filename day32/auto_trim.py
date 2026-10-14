"""
对话太长了自动压缩

中间件：SummarizationMiddleware
"""

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver


with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


model = ChatDeepSeek(model = "deepseek-chat",api_key=ds_key)

agent = create_agent(
    model,
    tools=[],
    system_prompt="你是一个助手，回答简短。",
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model = model,
            trigger=("tokens", 60),
            keep=("messages", 2),
        ),
    ],
)

config = {"configurable":{"thread_id":"T"}}

def ask(text):
    result = agent.invoke(
        {"messages":[{"role":"user","content":text}]},
        config=config,
    )
    return result["messages"][-1].content,result["messages"]

for q in ["我叫小明", "我在做 AI 开发", "我最近在学 RAG", "我叫什么？在做什么？"]:
    answer, msgs = ask(q)
    print("=" * 62)
    print(f"我：{q}")
    print(f"AI：{answer[:70]}")
    for m in msgs:
        print(f"       {type(m).__name__:<16} {str(m.content)[:55]}")
    print()