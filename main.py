import json
from fastapi.responses import JSONResponse

@app.post("/api/books")
async def get_similar_books(book: BookRequest):
    try:
        prompt = f"""
        次の本と類似する書籍を3冊リストアップしてください。

        タイトル: {book.title}
        読み仮名: {book.reading}
        著者: {book.author}

        以下のJSON形式で出力してください:
        {{
          "similar_books": [
            {{"title": "", "author": ""}},
            {{"title": "", "author": ""}},
            {{"title": "", "author": ""}}
          ]
        }}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content

        # ChatGPTの返答をJSONパース
        result_json = json.loads(content)
        return JSONResponse(content=result_json)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
