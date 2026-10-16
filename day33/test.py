"""
自己搭一张带分支的图

对比 create_agent：
    那个是「model ↔ tools」写死的循环
    这个能自己加岔路
"""


from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_deepseek import ChatDeepSeek

with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


model = ChatDeepSeek(model="deepseek-flash",api_key=ds_key,timeout=60, max_retries=1,)

class 状态(TypedDict):
    问题:str
    类别:str
    答案:str


def 判断(state):
    print(f"      [判断] 收到：{state}")  
    q = state["问题"]
    prompt = (
        "把用户的这句话分成三类，只回一个词（不要标点、不要解释）:\n"
        "  笔记 --在问某个知识点是什么、怎么用（比如RAG、函数、异常处理）\n"
        "  算数 --需要做数学计算\n"
        "  闲聊 --其他（打招呼、闲聊、问天气）\n\n"
        f"用户：{q}\n"
        "分类："
    )
    r = model.invoke(prompt)
    类别 = r.content.strip().replace(": ", " ").replace(" ", "")
    print(f"      [判断] 返回 {类别!r}")  
    return {"类别": 类别}

def 路由(state):
    print(f"      [路由] 收到：{state}") 
    return state["类别"]

def 查笔记(state):
    print(f"      [查笔记] 收到：{state}")   
    return {"答案":f"【走「查笔记」这条路】去检索笔记里关于「{state['问题']}」的内容"}

def 算数(state):
    print(f"      [算数] 收到：{state}")
    return {"答案":f"【走「算数」这条路】调用计算器算「{state['问题']}」"}

def 闲聊(state):
    print(f"      [闲聊] 收到：{state}") 
    return {"答案": f"【走「闲聊」这条路】直接聊「{state['问题']}」"}

builder = StateGraph(状态)



builder.add_node("判断",判断)
builder.add_node("查笔记",查笔记)
builder.add_node("算数",算数)
builder.add_node("闲聊",闲聊)

builder.add_edge(START, "判断")

builder.add_conditional_edges(
    "判断",
    路由,
    {
        "笔记":"查笔记",
        "算数":"算数",
        "闲聊":"闲聊",
    },
)

builder.add_edge("查笔记", END)
builder.add_edge("算数", END)
builder.add_edge("闲聊", END)

graph = builder.compile()


for q in ["RAG 是什么", "12 加 30 等于几", "今天天气不错"]:
    print("=" * 62)
    print(f"问：{q}")
    print("=" * 62)

    out = graph.invoke({"问题":q})
    print(f"  分类节点判定为：{out['类别']}")
    print(f"  实际走到：{out['答案']}")
    print()

