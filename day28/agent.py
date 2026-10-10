"""
给模型加上「手」：读文件、写文件、列目录

★ 重点在 safe_path —— 模型只能在我们划定的文件夹里活动。
"""


import json
import os
import requests
import math

WORD_DIR = "工作区"
INDEX_FILE = "index.json"
TOP_K = 5

with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()
with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


def safe_path(filename):
    base = os.path.abspath(WORD_DIR)
    path = os.path.abspath(os.path.join(WORD_DIR, filename))
    if not path.startswith(base):
        raise ValueError(f"不允许访问工作目录之外的路径：{filename}")
    return path

def list_files():
    names = sorted(os.listdir(WORD_DIR))
    if not names:
        return "（工作目录是空的）"
    return "\n".join(names)

def read_file(filename):
    try:
        path = safe_path(filename)
    except ValueError as e:
        return f"读取失败:{e}"
    if not os.path.exists(path):
        return f"文件不存在:{filename}"
    if os.path.isdir(path):
        return f"{filename} 是一个文件夹，不是文件。用 list_files 看看里面有什么。"
    with open(path, encoding="utf-8")as f:
        return f.read()



def write_file(filename, content):
    try:
        path = safe_path(filename)
    except ValueError as e:
        return f"写入失败：{e}"
    folder =os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with open(path,"w",encoding="utf-8")as f:
        f.write(content)
    return f"以写入 {filename}({len(content)} 个字符)"



def embed_batch(texts):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sf_key}",
            "Content-Type":"application/json",
        },
        json={"model":"BAAI/bge-m3","input":texts},
        timeout=60
    )
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors


def cosine(a, b):
    dot = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
    len_a = 0
    for x in a:
        len_a += x * x
    len_b = 0
    for x in b:
        len_b += x * x
    return dot/(math.sqrt(len_b)*math.sqrt(len_a))


with open(INDEX_FILE,encoding="utf-8")as f:
    _data = json.load(f)

CHUNKS = _data["chunks"]
VECTORS = _data["vectors"]

def search_notes(question):
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(VECTORS)):#######CHUNKS
        scores.append((cosine(q_vec, VECTORS[i]), i))
    scores.sort(reverse=True)
    text = ""
    for score, i in scores[:TOP_K]:
        c = CHUNKS[i]
        text += f"【来源：{c['source']}】\n{c['text']}\n\n"
    return text


TOOLS = [
    {
        "type":"function",
        "function":{
            "name":"list_files",
            "description":"列出工作目录里有哪些文件。想知道有哪些文件可读时调用。",
            "parameters":{"type":"object","properties":{}},
        },
    },

    {
        "type":"function",
        "function":{
            "name":"read_file",
            "description":"读取工作目录里某个文件的完整内容。想查看某个文件的原文时调用。",
            "parameters":{  
                "type":"object",
                "properties":{
                    "filename":{
                        "type":"string",
                        "description":"文件名，比如 第4天-学习笔记.md",
                    },
                },
                "required":["filename"],
            },
        },
    },

    {
        "type":"function",
        "function":{
            "name":"write_file",
            "description":(
                "把内容写成一个新文件保存在工作目录里。"
                "当用户要求整理、汇总、保存成文件时调用。"
            ),
            "parameters":{
                "type":"object",
                "properties":{
                    "filename":{"type":"string","description":"文件名"},
                    "content":{"type":"string","description":"要写入的完整内容"},
                },
                "required":["filename","content"],
            },
        },
    },

    {
        "type":"function",
        "function":{
            "name":"search_notes",
            "description":(
                 "在所有笔记里做语义检索，返回最相关的片段。"
                "想知道某个知识点散落在哪些笔记里时调用。"
            ),
            "parameters":{
                "type":"object",
                "properties":{
                    "question":{"type":"string","description":"要检索的问题"},
                },
                "required":["question"],
            },
        },
    },
]


FUNCS = {
    "list_files":list_files,
    "read_file":read_file,
    "write_file":write_file,
    "search_notes":search_notes,
}

MAX_ROUNDS = 10
SYSTEM_PROMPT = (
    "只在这个问题涉及用户学习笔记里的知识点时调用。\n"
    "如果是生活常识、闲聊、通用知识，不要调用。\n"
    "你是一个学习助手，可以读写工作目录里的文件，也能检索笔记。\n"
    "用户会给你一个【目标】，不是一个问题。\n"
    "\n"
    "你需要自己想清楚分几步做，然后用工具一步一步完成：\n"
    "- 先看看有什么可用（list_files）\n"
    "- 不知道在哪就检索（search_notes）\n"
    "- 知道是哪个文件就去读（read_file）\n"
    "- 需要产出就写出去（write_file）\n"
    "\n"
    "做完了再给最终答复，说明你做了什么、结果在哪。"
    )

def call_model(messages):
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization":f"Bearer {ds_key}",
            "Content-Type":"application/json",
        },
        json={"model":"deepseek-chat","messages":messages,"tools":TOOLS},
        timeout=90,
    )
    return response.json()["choices"][0]

def run_agent(goal):
    """跑一个目标，返回 (最终答案, 过程记录)

    跟 day26 的 run() 比：
        day26  run()       →  print 出来给人看
        day28  run_agent() →  return 出去，给别的程序用
    """
    messages = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":goal},
    ]
    steps = []
    for n in range(1 , MAX_ROUNDS+1):
        choice = call_model(messages)
        msg = choice["message"]
        if choice["finish_reason"] != "tool_calls":
            return msg["content"], steps

        messages.append(msg)
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            result = FUNCS[name](**args)
            steps.append({
                "round":n,
                "tool":name,
                "args":args,
            })
            messages.append({
                "role":"tool",
                "tool_call_id":tc["id"],
                "content":str(result)
            })
    return "（到轮数上限了，没做完）", steps
