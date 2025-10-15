import requests
import xmltodict

def search_ndl_books(keyword: str, count: int = 5):
    url = "https://ndlsearch.ndl.go.jp/api/opensearch"
    params = {
        "title": keyword,
        "cnt": count,
        "format": "xml"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = xmltodict.parse(response.text)
    items = data['rss']['channel'].get('item', [])
    if isinstance(items, dict):
        items = [items]

    return [
        {
            "title": item.get("title", "タイトル不明"),
            "author": item.get("dc:creator", "著者不明")
        }
        for item in items
    ]