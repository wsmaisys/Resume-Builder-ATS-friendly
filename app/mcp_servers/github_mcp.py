import asyncio

from mcp.server.fastmcp import FastMCP

from app.config import get_settings
from app.services.github_service import GitHubService


mcp = FastMCP("resume-builder-github")


@mcp.tool()
async def fetch_github_profile(username: str | None = None) -> dict:
    """Fetch GitHub profile, repos, README excerpts, and recent commits."""
    settings = get_settings()
    return await GitHubService().fetch_profile(username or settings.github_username)


def main() -> None:
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
