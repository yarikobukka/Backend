import asyncio
from fastapi import FastAPI
from asgiref.compatibility import guarantee_single_callable
from asgiref.wsgi import WsgiMiddleware
from werkzeug.wrappers import Request, Response

# FastAPI アプリ作成
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI with self-made adapter"}

# OpenAI クライアント利用例
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/ai")
async def ai_route():
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "東方プロジェクトの古明地さとりについて教えて"
            }
        ]
    )
    return {"story": response.choices[0].message.content}

# ASGI → WSGI 変換
asgi_app = guarantee_single_callable(app)
wsgi_app = WsgiMiddleware(asgi_app)

# Vercel が呼ぶ handler
def handler(environ, start_response):
    return wsgi_app(environ, start_response)


