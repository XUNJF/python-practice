import sqlite3

DB = "learn.db"

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def create_table():
    c = connect()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer   TEXT NOT NULL,
            created  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.commit()
    c.close()


def save(question, answer):
    c = connect()
    c.execute(
        "INSERT INTO history (question, answer) VALUES (?, ?)",
        (question, answer),
    )
    c.commit()
    c.close()

def recent(n=5):
    c = connect()
    cur = c.execute(
        "SELECT id, question, answer, created FROM history ORDER BY id DESC LIMIT ?",
        (n,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    c.close()
    return rows

def count():
    c = connect()
    n = c.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    c.close()
    return n

if __name__ == "__main__":
    create_table()
    print("建表完成，现在有", count(), "条")
    save("RAG 是什么？", "检索增强生成")
    save("8472+3951 是多少", "12423")
    save("我是小明", "你好小明")
    print("写入 3 条，现在有", count(), "条")

    print()
    print("最近 5 条：")
    for r in recent():
        print(f"  [{r['id']}] {r['created']}")
        print(f"       问：{r['question']}")
        print(f"       答：{r['answer'][:30]}")