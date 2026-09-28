from fastapi import FastAPI
from chat_bot import ChatBot
from fastapi.responses import FileResponse

app = FastAPI()
bot = ChatBot("你是一个Python助教，回答控制在50字以内") 

@app.get("/")
def index():
    return FileResponse("index.html")



@app.post("/chat")
def chat(question:str):
    answer = bot.chat(question)
    return {"answer":answer}