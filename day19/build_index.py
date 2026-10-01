import os
import json
import requests

NOTES_DIR = "../../学习笔记"
INDEX_FILE = "index.json"
MIN_LEN = 50
BATCH_SIZE = 20

with open("key_sf.txt","r",encoding="utf-8")as f:
    sf_key = f.read().strip()


def embed_batch(texts):
    """把一批文字转成向量，返回一批向量"""
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sf_key}",
            "Content-Type":"application/json",
        },
        json = {"model":"BAAI/bge-m3","input":texts},
        timeout=60,
    )
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors

def cut_into_chunks():
    """遍历笔记文件夹，按 ## 标题把每个 .md 切成小块"""
    chunks = []
    for filename in sorted(os.listdir(NOTES_DIR)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(NOTES_DIR,filename)
        with open(path,"r",encoding="utf-8")as f:
            content = f.read()

        parts = content.split("\n## ")
        for i, part in enumerate(parts):
            if i == 0:
                text = part
            else:
                text = "## "+part

            text = text.strip()
            if text.endswith("---"):
                text = text[:-3].strip()
            if len(text) < MIN_LEN:
                continue

            chunks.append({
                "text":text,
                "source":filename,
            })
    return chunks




print("第1步：读笔记、切分……")
chunks = cut_into_chunks()
print(f" 切出{len(chunks)} 块")

print()
print(f"第2步：转向量（每批{BATCH_SIZE} 段，要等一会）……")

all_texts = [c["text"] for c in chunks]
all_vectors = []

for start in range(0,len(all_texts),BATCH_SIZE):
    batch = all_texts[start:start+BATCH_SIZE]
    all_vectors.extend(embed_batch(batch))
    done = min(start+BATCH_SIZE,len(all_texts))
    print(f" 已完成{done}/{len(all_texts)}")

print()
print(f"第3步：存进{INDEX_FILE}……")

with open(INDEX_FILE,"w",encoding="utf-8") as f:
    json.dump(
        {"chunks":chunks,"vectors":all_vectors},
        f,
        ensure_ascii=False,
        indent=2,
    )

size = os.path.getsize(INDEX_FILE)/1024/1024
print(f"  完成，文件大小 {size:.1f} MB")
print()
print("以后直接用 ask_notes.py 提问，不用再跑这个。")