from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI()
@app.get("/")
def read_root():

    response = client.responses.create(
    model="gpt-4.1",
    input="Tell me a three sentence bedtime story about a unicorn."
    )

    return response