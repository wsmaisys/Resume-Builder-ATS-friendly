import asyncio
from typing import Annotated, Any
from urllib.parse import urljoin

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from app.config import get_settings
from app.mcp_servers.contracts import error_response, ok_response
from app.services.portfolio_service import PortfolioService


SERVER_INSTRUCTIONS = """
Use this MCP server whenever a resume, cover letter, project list, or candidate profile needs current public portfolio evidence for Wasim Ansari.
Prefer candidate_portfolio_project_links when the task needs live demos, GitHub URLs, profile links, or publication URLs.
Use candidate_portfolio_content when the task needs the current visible text from the portfolio page.
All tools are read-only, non-destructive, and safe to call repeatedly. Never invent portfolio claims or deployed links.
"""

PORTFOLIO_USAGE = (
    "Use portfolio text and links as current public evidence. "
    "For resume generation, combine this data with master_profile.json and GitHub data, and treat missing links as unknown rather than fabricated."
)


mcp = FastMCP(
    "resume-builder-portfolio",
    instructions=SERVER_INSTRUCTIONS,
)


async def _fetch(url: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    selected_url = url or settings.portfolio_url
    data = await PortfolioService().fetch(selected_url)
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    return data


def _absolute_links(base_url: str, links: list[dict[str, Any]]) -> list[dict[str, str]]:
    output = []
    for link in links:
        href = str(link.get("href") or "").strip()
        text = str(link.get("text") or "").strip()
        if not href:
            continue
        output.append({"text": text, "url": urljoin(base_url, href)})
    return output


@mcp.tool(
    name="candidate_portfolio_content",
    title="Candidate Portfolio Content",
    description=(
        "Fetch the current visible text and links from Wasim Ansari's public portfolio page. "
        "Use this for profile refresh, resume tailoring, cover letters, and project summaries that need current portfolio claims. "
        "Returns normalized text and absolute links. Use candidate_portfolio_project_links if you only need demos/repo/publication links."
    ),
    annotations=ToolAnnotations(
        title="Fetch candidate portfolio content",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    structured_output=True,
)
async def candidate_portfolio_content(
    url: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional portfolio URL. Leave empty to use the configured candidate portfolio URL.",
            examples=["https://wsmaisys.github.io/waseemmansari.github.io/"],
        ),
    ] = None,
) -> dict[str, Any]:
    try:
        data = await _fetch(url)
        return ok_response(
            {
                "url": data.get("url"),
                "text": data.get("text", ""),
                "text_char_count": len(data.get("text", "")),
                "links": _absolute_links(data.get("url", ""), data.get("links", [])),
            },
            PORTFOLIO_USAGE,
        )
    except Exception as exc:
        return error_response(str(exc), PORTFOLIO_USAGE, {"url": url})


@mcp.tool(
    name="candidate_portfolio_project_links",
    title="Candidate Portfolio Project Links",
    description=(
        "Fetch current public links from the candidate portfolio and group them by use: live demos, GitHub repos, MCP endpoints, Docker artifacts, publications, and external profiles. "
        "Use this when a resume agent needs exact deployment URLs or proof links for portfolio projects. "
        "Optionally pass link_query such as 'MediFlow', 'Jurisol', 'GitHub', or 'Live Demo' to filter."
    ),
    annotations=ToolAnnotations(
        title="Fetch candidate portfolio project links",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    structured_output=True,
)
async def candidate_portfolio_project_links(
    link_query: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional case-insensitive filter over link text and URL. Leave empty to return all portfolio links.",
            examples=["Live Demo", "MediFlow", "GitHub"],
        ),
    ] = None,
    url: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional portfolio URL. Leave empty to use configured candidate portfolio URL.",
        ),
    ] = None,
) -> dict[str, Any]:
    try:
        data = await _fetch(url)
        query = (link_query or "").lower().strip()
        links = _absolute_links(data.get("url", ""), data.get("links", []))
        if query:
            links = [
                link for link in links
                if query in f"{link['text']} {link['url']}".lower()
            ]

        grouped = {
            "live_demos": [],
            "github_repositories": [],
            "mcp_endpoints": [],
            "docker_artifacts": [],
            "publications": [],
            "external_profiles": [],
            "other_links": [],
        }
        for link in links:
            text = link["text"].lower()
            value = link["url"].lower()
            if "github.com/wsmaisys/" in value:
                grouped["github_repositories"].append(link)
            elif "live demo" in text or any(host in value for host in ("run.app", "onrender.com", "streamlit.app", "azurewebsites.net", "huggingface.co/spaces")):
                grouped["live_demos"].append(link)
            elif "mcp" in text or value.endswith("/mcp") or "/mcp" in value:
                grouped["mcp_endpoints"].append(link)
            elif "hub.docker.com" in value or "docker" in text:
                grouped["docker_artifacts"].append(link)
            elif "linkedin.com/pulse" in value or "medium.com" in value:
                grouped["publications"].append(link)
            elif any(host in value for host in ("linkedin.com/in", "kaggle.com", "europass", "github.com/wsmaisys")):
                grouped["external_profiles"].append(link)
            else:
                grouped["other_links"].append(link)

        return ok_response(
            {
                "query": link_query,
                "result_count": len(links),
                "links": links,
                "grouped_links": grouped,
            },
            PORTFOLIO_USAGE,
        )
    except Exception as exc:
        return error_response(str(exc), PORTFOLIO_USAGE, {"url": url, "link_query": link_query})


@mcp.tool(
    name="fetch_portfolio_content",
    title="Backward Compatible Portfolio Content Fetch",
    description=(
        "Backward-compatible alias for candidate_portfolio_content. "
        "Prefer candidate_portfolio_content or candidate_portfolio_project_links in new prompts because they have clearer contracts."
    ),
    annotations=ToolAnnotations(
        title="Fetch portfolio compatibility alias",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    structured_output=True,
)
async def fetch_portfolio_content(
    url: Annotated[
        str | None,
        Field(default=None, description="Optional portfolio URL. Leave empty to use configured candidate portfolio URL."),
    ] = None,
) -> dict[str, Any]:
    return await candidate_portfolio_content(url=url)


def main() -> None:
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
