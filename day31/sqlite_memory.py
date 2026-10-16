"""
把记忆存到硬盘上

跟 day30 的区别：InMemorySaver → SqliteSaver
效果：程序关掉再打开，它还认识你
"""

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.sqlite import SqliteSaver

with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


model = ChatDeepSeek(model = "deepseek-flash", api_key=ds_key)

with SqliteSaver.from_conn_string("记忆.db")as checkpointer:

    agent = create_agent(
        model,
        tools=[],
        system_prompt="你是一个助手，回答简短点。",
        checkpointer=checkpointer,
    )
    def ask(text, thread):
        config = {"configurable":{"thread_id":thread}}
        result = agent.invoke(
            {"messages":[{"role":"user","content":text}]},
            config = config,
        )
        return result["messages"][-1].content
    print("  我：我叫小明，在做 AI 开发")
    print("  AI：", ask("我叫小明，在做 AI 开发", "A"))
    print()
    print("  我：我叫什么？在做什么？")
    print("  AI：", ask("我叫什么？在做什么？", "A"))
    print()