import requests
import os
import json


class ChatBot:
    def __init__(self,system_prompt):
        with open("key.txt","r",encoding="utf-8")as f:
            self.api_key = f.read().strip()

        self.headers = {
            "Authorization":f"Bearer {self.api_key}",
            "Content-Type":"application/json",
        }
        self.messages = [{"role":"system","content":system_prompt}]

    def chat(self,question):
        self.messages.append({"role":"user","content":question})
        payload = {
            "model":"deepseek-chat",
            "messages":self.messages,
        }
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers= self.headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            answer =data["choices"][0]["message"]["content"]
            self.messages.append({"role":"assistant","content":answer})
            return answer
        else:
            print(f"状态码：{response.status_code}")
            print(f"原始状态：{response.text}")


    def save(self,filename):
        with open(filename,"w",encoding="utf-8")as f:
            json.dump(self.messages,f,ensure_ascii=False,indent=2)

    def load(self,filename):
        with open(filename,"r",encoding="utf-8")as f:
            self.messages = json.load(f)
        



bot = ChatBot("你是一个Python助教")

if os.path.exists("history.json"):
    bot.load("history.json")         

print(bot.chat("什么是变量？"))
bot.save("history.json")        





        