from fastapi import FastAPI
from chat_bot import ChatBot

app = FastAPI()

@app.get("/")
def read_root():
    return {"message":"你好，这是我的第一个接口"}

@app.get("/add")
def add(a:int,b:int):
    return {"result":a+b}

bot = ChatBot("你是一个Python助教，回答控制在50字以内")

@app.post("/chat")
def chat(question:str):
    answer = bot.chat(question)
    return {"answer":answer}