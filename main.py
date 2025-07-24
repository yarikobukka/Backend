from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # ← .envファイルから読み込み

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def ask_gpt():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # gpt-4oにしても可（API権限次第）
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "東方プロジェクトの各作品について教えて"}
        ]
    )
    return {"answer": response.choices[0].message.content}

