from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.sqlite import SqliteSaver


with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()

model = ChatDeepSeek(model = "deepseek-flash",api_key=ds_key)

with SqliteSaver.from_conn_string("记忆.db") as checkpointer:
    agent = create_agent(model, tools=[], system_prompt="你是一个助手，回答简单点。", checkpointer=checkpointer)
    config = {"configurable":{"thread_id":"A"}}
    result = agent.invoke(
        {"messages":[{"role":"user","content":"我叫什么？我在做什么？"}]},
        config=config,
    )
    print("  AI：",result["messages"][-1].content)