from flask import Flask, render_template_string
from openai import OpenAI
from dotenv import load_dotenv
import os

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

    html = f"""
    <html>
    <head><meta charset="utf-8"><title>古明地さとり解説</title></head>
    <body>
        <h1>古明地さとりについて</h1>
        <p>{story}</p>
    </body>
    </html>
    """
    return render_template_string(html)


