# """看看 记忆.db 里到底存了什么"""

# import sqlite3

# conn = sqlite3.connect("记忆.db")
# cur = conn.cursor()

# print("=" * 62)
# print("这个库里有哪些表")
# print("=" * 62)


# cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
# for (name,) in cur.fetchall():
#     print(f"  {name}")

# print()


# print("=" * 62)
# print("checkpoints 表：每个会话存了几版，一版接一版")
# print("=" * 62)
# print()


# cur.execute("SELECT thread_id, COUNT(*) FROM checkpoints GROUP BY thread_id")
# for tid, n in cur.fetchall():
#     print(f"  thread_id={tid!r}   存了 {n} 版")

# print()
# print("  最近 5 版（看它们是怎么串起来的）：")
# print()

# cur.execute("""
#     SELECT thread_id, checkpoint_id, parent_checkpoint_id
#     FROM checkpoints
#     ORDER BY checkpoint_id DESC
#     LIMIT 5
# """)
# for tid, cid, pid in cur.fetchall():
#     print(f"    {tid}  这一版 {cid[:12]}...  ←  上一版 {str(pid)[:12]}...")

# conn.close()

"""把存档里的对话内容解出来"""

import sqlite3
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

conn = sqlite3.connect("记忆.db")
cur = conn.cursor()
cur.execute("SELECT checkpoint FROM checkpoints ORDER BY checkpoint_id DESC LIMIT 1")
blob = cur.fetchone()[0]
conn.close()

serde = JsonPlusSerializer()
data = serde.loads_typed(("msgpack", blob))

print(f"  解开了，messages 里有 {len(data['channel_values']['messages'])} 条：")
print()
for m in data["channel_values"]["messages"]:
    kind = type(m).__name__
    text = str(getattr(m, "content", ""))[:60].replace("\n", " ")
    print(f"    {kind:<16} {text}")