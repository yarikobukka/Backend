import requests

def search_google_books(keyword: str, count: int = 10):
    url = "https://www.googleapis.com/books/v1/volumes"

    params = {
        "q": keyword,
        "maxResults": count,
        "printType": "books",
        "langRestrict": "ja"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Google Books API リクエスト失敗: {e}")
        return []

    data = response.json()

    if "items" not in data:
        return []

    books = []
    for item in data["items"]:
        info = item.get("volumeInfo", {})

        title = info.get("title", "タイトル不明")
        authors = info.get("authors", ["著者不明"])

        books.append({
            "title": title,
            "author": ", ".join(authors)
        })

    return books