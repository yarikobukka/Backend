from flask import Flask, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "東方プロジェクトの古明地さとりについて教えて"
            }
        ]
    )
    story = response.choices[0].message.content

    # ensure_ascii=False で日本語をそのまま返す
    return Response(
        json.dumps({"story": story}, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)

