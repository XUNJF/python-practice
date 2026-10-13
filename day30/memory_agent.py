"""
给 Agent 加上记忆

对比：
    day29  →  每次 invoke 都是全新的，它不认识你
    day30  →  同一个 thread_id 里，它记得之前说过什么
"""


from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver


with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


model = ChatDeepSeek(model = "deepseek-chat",api_key=ds_key)

agent = create_agent(
    model,
    tools=[],
    system_prompt="你是一个助手，回答简短点。",
    checkpointer=InMemorySaver(),
)

def ask(text, thread):
    config = {"configurable":{"thread_id":thread}}
    result = agent.invoke(
        {"messages":[{"role":"user","content":text}]},
        config=config,
    )
    return result["messages"][-1].content


print("=" * 62)
print("会话 A")
print("=" * 62)

print("  我：我叫小明，在做 AI 开发")
print("  AI：", ask("我叫小明，在做 AI 开发", "A"))
print()

print("  我：我叫什么？在做什么？")
print("  AI：", ask("我叫什么？在做什么？", "A"))
print()

print("=" * 62)
print("会话 B（换个 thread_id）")
print("=" * 62)

print("  我：我叫什么？")
print("  AI：", ask("我叫什么？", "B"))
print()

print("=" * 62)
print("回到会话 A，看它还记得吗")
print("=" * 62)

print("  我：我刚才说我叫什么来着？")
print("  AI：", ask("我刚才说我叫什么来着？", "A"))
print()