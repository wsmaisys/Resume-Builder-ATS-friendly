import asyncio

from mcp.server.fastmcp import FastMCP

from app.config import get_settings
from app.services.portfolio_service import PortfolioService


mcp = FastMCP("resume-builder-portfolio")


@mcp.tool()
async def fetch_portfolio_content(url: str | None = None) -> dict:
    """Fetch current portfolio page text and links for profile enrichment."""
    settings = get_settings()
    return await PortfolioService().fetch(url or settings.portfolio_url)


def main() -> None:
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
