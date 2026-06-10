from bs4 import BeautifulSoup
import httpx


class PortfolioService:
    async def fetch(self, url: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = " ".join(soup.get_text(" ").split())
            links = [
                {"text": a.get_text(" ", strip=True), "href": a.get("href")}
                for a in soup.find_all("a", href=True)
            ]
            return {"url": url, "text": text[:12000], "links": links}
        except Exception as exc:
            return {"url": url, "error": str(exc), "text": "", "links": []}
