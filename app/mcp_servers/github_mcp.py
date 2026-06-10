import asyncio
import re
from typing import Annotated, Any
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from app.config import get_settings
from app.mcp_servers.contracts import compact_repo, error_response, ok_response
from app.services.github_service import GitHubService


SERVER_INSTRUCTIONS = """
Use this MCP server whenever a resume, cover letter, portfolio summary, or candidate profile needs current GitHub evidence for Wasim Ansari.
Prefer candidate_github_repository_catalog for broad repo evidence and candidate_github_project_links when the task needs live demo/deployment URLs.
All tools are read-only, non-destructive, and safe to call repeatedly. If a tool returns ok=false, use the error.message and retry only after changing the input or network/auth condition.
Never invent repository URLs, deployed URLs, commit details, stars, or languages. Use only returned data.
"""

GITHUB_USAGE = (
    "Use returned repo_url, deployed_urls, artifact_urls, README excerpts, and recent_commits as evidence. "
    "For resume tailoring, cite only projects relevant to the target job and do not claim skills that are not supported by profile or repository evidence."
)

APP_HOST_PARTS = (
    "run.app",
    "onrender.com",
    "streamlit.app",
    "azurewebsites.net",
    "huggingface.co/spaces",
    "hyrefast.ai",
    "zovia.ai",
    "github.io",
)
ARTIFACT_HOST_PARTS = ("hub.docker.com",)
IGNORE_URL_PARTS = (
    "localhost",
    "127.0.0.1",
    "img.shields.io",
    "capsule-render",
    "git.io",
    "console.mistral.ai",
    "docs.crewai.com",
    "fastapi.tiangolo.com",
    "ffmpeg.org",
    "python.org",
    "docker.com",
    "opensource.org",
    "mistral.ai",
    "langchain.com",
    "cloud.google.com",
    "huggingface.co/black-forest-labs",
)
URL_RE = re.compile(r"https?://[^\s)\]}>\"'`]+")


mcp = FastMCP(
    "resume-builder-github",
    instructions=SERVER_INSTRUCTIONS,
)


def _clean_url(url: str) -> str:
    return url.strip().rstrip(".,;`")


def _is_app_url(url: str) -> bool:
    value = _clean_url(url).lower()
    host = urlparse(value).netloc
    return (
        value.startswith("http")
        and bool(host)
        and not any(part in value for part in IGNORE_URL_PARTS)
        and any(part in value for part in APP_HOST_PARTS)
    )


def _is_artifact_url(url: str) -> bool:
    value = _clean_url(url).lower()
    return value.startswith("http") and any(part in value for part in ARTIFACT_HOST_PARTS)


def _enrich_repo_links(repo: dict[str, Any]) -> dict[str, Any]:
    readme_urls = sorted(set(_clean_url(url) for url in URL_RE.findall(repo.get("readme") or "")))
    repo["readme_urls"] = readme_urls
    repo["deployed_urls"] = sorted({url.rstrip("/") for url in readme_urls if _is_app_url(url)})
    repo["artifact_urls"] = sorted({url.rstrip("/") for url in readme_urls if _is_artifact_url(url)})
    return repo


async def _fetch(username: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    selected_username = username or settings.github_username
    data = await GitHubService().fetch_profile(selected_username)
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    for repo in data.get("repos", []):
        _enrich_repo_links(repo)
    return data


@mcp.tool(
    name="candidate_github_repository_catalog",
    title="Candidate GitHub Repository Catalog",
    description=(
        "Fetch current GitHub evidence for Wasim Ansari or a supplied GitHub username. "
        "Use this before tailoring resumes, cover letters, project summaries, or profile refreshes that need current repository facts. "
        "Returns profile metadata and a compact catalog of repositories with repo URLs, descriptions, languages, stars, forks, topics, update dates, deployed links, artifact links, and recent commits. "
        "Do not use this for generic web search. Do not fabricate missing deployment links."
    ),
    annotations=ToolAnnotations(
        title="Fetch candidate GitHub repository catalog",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    structured_output=True,
)
async def candidate_github_repository_catalog(
    username: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional GitHub username. Leave empty to use the configured candidate username from app settings.",
            examples=["wsmaisys"],
        ),
    ] = None,
) -> dict[str, Any]:
    try:
        data = await _fetch(username)
        return ok_response(
            {
                "profile": data.get("profile", {}),
                "repository_count": len(data.get("repos", [])),
                "repositories": [compact_repo(repo) for repo in data.get("repos", [])],
            },
            GITHUB_USAGE,
        )
    except Exception as exc:
        return error_response(str(exc), GITHUB_USAGE, {"username": username})


@mcp.tool(
    name="candidate_github_project_links",
    title="Candidate GitHub Project Links",
    description=(
        "Fetch repository and deployment links for candidate projects. "
        "Use this when an LLM needs exact GitHub repo URLs, live demo URLs, Cloud Run/Render/Streamlit/Azure/Hugging Face links, or Docker artifacts for portfolio projects. "
        "Optionally provide a project_query such as 'MediFlow', 'Jurisol', or 'RAG' to filter results. "
        "The tool is read-only and returns evidence only; absence of a deployed URL means none was found."
    ),
    annotations=ToolAnnotations(
        title="Fetch candidate project repo and deployment links",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    structured_output=True,
)
async def candidate_github_project_links(
    project_query: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional case-insensitive project or keyword filter. Leave empty to return all repos with link evidence.",
            examples=["MediFlow", "RAG", "FastAPI"],
        ),
    ] = None,
    username: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional GitHub username. Leave empty to use the configured candidate username.",
            examples=["wsmaisys"],
        ),
    ] = None,
) -> dict[str, Any]:
    try:
        data = await _fetch(username)
        query = (project_query or "").lower().strip()
        projects = []
        for repo in data.get("repos", []):
            haystack = " ".join(
                str(value or "")
                for value in [
                    repo.get("name"),
                    repo.get("description"),
                    repo.get("language"),
                    " ".join(repo.get("topics", [])),
                    repo.get("readme", "")[:1000],
                ]
            ).lower()
            if query and query not in haystack:
                continue
            projects.append(compact_repo(repo))
        return ok_response(
            {
                "query": project_query,
                "result_count": len(projects),
                "projects": projects,
            },
            GITHUB_USAGE,
        )
    except Exception as exc:
        return error_response(str(exc), GITHUB_USAGE, {"username": username, "project_query": project_query})


@mcp.tool(
    name="fetch_github_profile",
    title="Backward Compatible GitHub Profile Fetch",
    description=(
        "Backward-compatible alias for candidate_github_repository_catalog. "
        "Prefer candidate_github_repository_catalog in new prompts because it has a clearer contract."
    ),
    annotations=ToolAnnotations(
        title="Fetch GitHub profile compatibility alias",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    structured_output=True,
)
async def fetch_github_profile(
    username: Annotated[
        str | None,
        Field(default=None, description="Optional GitHub username. Leave empty to use configured candidate username."),
    ] = None,
) -> dict[str, Any]:
    return await candidate_github_repository_catalog(username=username)


def main() -> None:
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
