import requests
from bs4 import BeautifulSoup
from langchain.tools import BaseTool

from config import config

BASE_URL = config.SARJ_WEB_URL.rstrip("/")

PAGE_ROUTES = {
    "contact": "/contact-us",
    "about": "/about-us",
    "terms": "/terms-conditions",
    "privacy": "/privacy-policy",
}


def _fetch_page(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"[Failed to fetch {url}: {e}]"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "head"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


class SarjSearch(BaseTool):
    name: str = "sarj_search"
    description: str = (
        "Use this tool to look up information about Sarj — contact details, "
        "services, products, pricing, about us, or any other details. "
        "Input should be a question or topic."
    )

    def _run(self, query: str) -> str:
        query_lower = query.lower()

        pages_to_fetch = [BASE_URL]
        for keyword, route in PAGE_ROUTES.items():
            if keyword in query_lower:
                pages_to_fetch.append(BASE_URL + route)

        results = []
        char_budget = 4000
        for url in pages_to_fetch:
            text = _fetch_page(url)
            chunk = text[:char_budget]
            results.append(f"[Source: {url}]\n{chunk}")
            char_budget -= len(chunk)
            if char_budget <= 0:
                break

        return "\n\n".join(results)