import requests
from bs4 import BeautifulSoup
from langchain.tools import BaseTool

from config import config

BASE_URL = config.SARJ_WEB_URL.rstrip("/")

ALWAYS_FETCH = [BASE_URL]

KEYWORD_ROUTES = {
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


def _get_internal_links(html: str) -> list[str]:
    """Extract all internal links from a page's HTML."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(BASE_URL):
            links.add(href.rstrip("/"))
        elif href.startswith("/") and not href.startswith("//"):
            links.add(BASE_URL + href.rstrip("/"))
    return [l for l in links if l.startswith("http")]


def _score_url(url: str, query_lower: str) -> int:
    """Score a URL by how relevant it looks to the query."""
    url_lower = url.lower()
    score = 0
    for word in query_lower.split():
        if word in url_lower:
            score += 2

    for keyword in ["product", "service", "price", "contact", "about", "equestrian", "clothes", "mask", "glasses"]:
        if keyword in url_lower and keyword in query_lower:
            score += 3
    return score


class SarjSearch(BaseTool):
    name: str = "sarj_search"
    description: str = (
        "Use this tool to look up information about Sarj — contact details, "
        "services, products, pricing, categories, about us, or any other details. "
        "Input should be a question or topic."
    )

    def _run(self, query: str) -> str:
        query_lower = query.lower()

        pages_to_fetch = list(ALWAYS_FETCH)

        for keyword, route in KEYWORD_ROUTES.items():
            if keyword in query_lower:
                pages_to_fetch.append(BASE_URL + route)

        try:
            homepage = requests.get(BASE_URL, timeout=10)
            homepage.raise_for_status()
            all_links = _get_internal_links(homepage.text)

            scored = sorted(all_links, key=lambda u: _score_url(u, query_lower), reverse=True)
            for link in scored[:3]:
                if link not in pages_to_fetch:
                    pages_to_fetch.append(link)
        except requests.RequestException:
            pass

        results = []
        char_budget = 5000
        for url in pages_to_fetch:
            text = _fetch_page(url)
            chunk = text[:char_budget]
            results.append(f"[Source: {url}]\n{chunk}")
            char_budget -= len(chunk)
            if char_budget <= 0:
                break

        return "\n\n".join(results)