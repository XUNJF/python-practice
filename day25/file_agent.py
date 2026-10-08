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
    return "/n".join(names)

def read_file(filename):
    try:
        path = safe_path(filename)
    except ValueError as e:
        return f"读取失败:{e}"
    if not os.path.exists(path):
        return f"文件不存在:{filename}"
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
    for item in range(len(texts)):
        vectors[item["index"]] = item["embedding"]
    return vectors


def cosine(a, b):
    dot = 0
    for i in len(a):
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


def run(question):
    print("="*62)
    print(f"目标：{question}")
    print("="*62)
    messages = [
        {"role":"system","content":"你是一个学习助手，可以读写工作目录里的文件。"},
        {"role":"user","content":question},
    ]

    n = 0
    while True:
        n += 1
        choice = call_model(messages)
        msg = choice["message"]
        if choice["finish_reason"] != "tool_calls":
            print(f"  (共{n}轮)")
            print()
            print(msg["content"])
            print()
            return
        messages.append(msg)
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args =json.loads(tc["function"]["arguments"])
            show = {}
            for k, v in args.items():
                if isinstance(v, str) and len(v) >40:
                    show[k] = v[:40] + "..."
                else:
                    show[k] = v
            print(f" [{n}]→{name}({show})")
            result = FUNCS[name](**args)
            messages.append({
                "role":"tool",
                "tool_call_id":tc["id"],
                "content":str(result)
            })


run("先看看工作目录里有什么文件")

run("把第4天那个笔记读出来，总结成五条要点，存成 第4天总结.md")