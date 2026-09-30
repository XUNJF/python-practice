import requests
import os
import json


message = []
class basics:
    
    with open("key_sf.txt","r",encoding="utf-8")as f:
        sk_api = f.read().strip()

    with open("history.json","w",encoding="utf-8")as f:
        json.dump(message,f, ensure_ascii=False,indent=2)
