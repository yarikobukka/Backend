from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/")
def read_root():
    response = client.chat.completions.create(
        model="gpt-4o",  # 正しいモデル名を指定
        messages=[
            {
                "role": "user",
                "content": "東方プロジェクトの作品である東方紅魔郷のストーリーについて解説して"
            }
        ]
    )
    return {"story": response.choices[0].message.content}

