"""
带循环的图：写代码 → 跑测试 → 不过就重写

跟 day33 的区别：
    多了一条指回去的边
    多了个「第几轮」当刹车
"""

import re
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_deepseek import ChatDeepSeek


with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


model = ChatDeepSeek(
    model="deepseek-flash",
    api_key=ds_key,
    timeout=60,
    max_retries=3,
)

test_cases = [
    ("1+2*3", 7),            # 优先级
    ("(1+2)*3", 9),          # 括号
    ("1/0", "不能除以零"),    # 除零要返回一句话，不能崩
    ("  2 + 3 ", 5),         # 空格
    ("+5", 5),               # 一元正号   
]

class State(TypedDict):
    code:str
    report:str
    round_num:int


def write_code(state:State):
    n = state.get("round_num", 0) + 1
    print(f"    -> write_code (第 {n} 稿)")
    rules=(
         "你是一个 Python 程序员。\n"
        "要求：\n"
        "  - 只输出一个 python 代码块，不要任何解释文字\n"
        "  - 函数名叫 calc，接收一个字符串参数 s\n"
        "  - 支持加减乘除、括号、运算优先级\n"
        "  - 遇到除以零，返回字符串「不能除以零」，不要抛异常\n"
    )
    if state.get("report"):
        user_msg = (
            f"你上一版写的：\n{state['code']}\n\n"
            f"测试结果：\n{state['report']}\n\n"
            "请修正后重新给出完整代码。"
        )
    else:
        user_msg = "写一个 Python 函数 calc(s)，计算字符串形式的算术表达式。"
    reply = model.invoke([
        {"role":"system","content":rules},
        {"role":"user","content":user_msg},
    ])
    match = re.search(r"```(?:python)?\n(.*?)```", reply.content, re.S)
    code = match.group(1) if match else reply.content
    return {"code":code,"round_num":n}


def run_tests(state:State):
    print("    -> run_tests")
    namespace = {}
    try:
        exec(state["code"], namespace)
        func = namespace["calc"]
        failures = []
        for arg, expected in test_cases:
            try:
                got = func(arg)
            except ZeroDivisionError:
                got = "不能除以零"
            except Exception as e:
                got = f"报错：{type(e).__name__}"
            if got != expected:
                failures.append(f"  calc({arg!r})应为{expected!r},实际{got!r}")
        report = "全部通过" if not failures else "\n".join(failures)
    except Exception as e:
        report = f"代码有问题：{type(e).__name__}:{e}"
    print(f"  {report[:70]}")
    return {"report":report}


def should_continue(state:State):
    if state["report"] == "全部通过" or state["round_num"] >= 4:
        return "done"
    return "retry"

builder = StateGraph(State)

builder.add_node("write_code", write_code)
builder.add_node("run_tests", run_tests)

builder.add_edge(START, "write_code")
builder.add_edge("write_code", "run_tests")

builder.add_conditional_edges(
    "run_tests",
    should_continue,
    {
        "retry":"write_code",
        "done":END,
    },
)

graph = builder.compile()


out = graph.invoke({})



print("="*62)
print(f"  一共写了 {out['round_num']} 稿")
print(f"  最终：{out['report']}")

print()
print(type(out))
# print(out)
print(repr(out))