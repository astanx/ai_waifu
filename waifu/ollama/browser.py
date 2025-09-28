import requests
from bs4 import BeautifulSoup

def fetch_duckduckgo_search_results(query: str) -> list[dict]:
    url = f"https://duckduckgo.com/html/?q={query}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    query_results = []
    # Iterate through search results
    for result in soup.select(".result"):
        title_tag = result.select_one(".result__a")
        snippet_tag = result.select_one(".result__snippet")
        url_tag = result.select_one(".result__url")  # For source/website name

        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
        else:
            continue

        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
        source = url_tag.get_text(strip=True) if url_tag else "Unknown source"


        data = {        "title": title,
            "link": link,
            "source": source,
            "snippet": snippet}
        query_results.append(data)

    print(f"Debug: DuckDuckGo fetched {len(query_results)} results")
    return query_results