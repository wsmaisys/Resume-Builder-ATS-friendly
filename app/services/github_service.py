import httpx
import base64

from app.config import get_settings


class GitHubService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_profile(self, username: str) -> dict:
        headers = {"Accept": "application/vnd.github+json"}
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"

        try:
            async with httpx.AsyncClient(timeout=30, headers=headers) as client:
                user_response = await client.get(f"https://api.github.com/users/{username}")
                repos_response = await client.get(
                    f"https://api.github.com/users/{username}/repos",
                    params={"sort": "updated", "per_page": 100},
                )
                user_response.raise_for_status()
                repos_response.raise_for_status()
                repos = repos_response.json()
                enriched_repos = []
                for repo in repos:
                    repo_name = repo.get("name")
                    enriched_repos.append(
                        {
                            "name": repo_name,
                            "description": repo.get("description"),
                            "language": repo.get("language"),
                            "stars": repo.get("stargazers_count"),
                            "forks": repo.get("forks_count"),
                            "updated_at": repo.get("updated_at"),
                            "created_at": repo.get("created_at"),
                            "topics": repo.get("topics", []),
                            "url": repo.get("html_url"),
                            "readme": await self._fetch_readme(client, username, repo_name),
                            "recent_commits": await self._fetch_recent_commits(client, username, repo_name),
                        }
                    )
                return {
                    "profile": user_response.json(),
                    "repos": enriched_repos,
                }
        except Exception as exc:
            return {"error": str(exc), "repos": []}

    async def _fetch_readme(self, client: httpx.AsyncClient, username: str, repo_name: str | None) -> str:
        if not repo_name:
            return ""
        try:
            response = await client.get(f"https://api.github.com/repos/{username}/{repo_name}/readme")
            if response.status_code == 404:
                return ""
            response.raise_for_status()
            data = response.json()
            content = data.get("content", "")
            if not content:
                return ""
            return base64.b64decode(content).decode("utf-8", errors="ignore")[:6000]
        except Exception:
            return ""

    async def _fetch_recent_commits(self, client: httpx.AsyncClient, username: str, repo_name: str | None) -> list[dict]:
        if not repo_name:
            return []
        try:
            response = await client.get(
                f"https://api.github.com/repos/{username}/{repo_name}/commits",
                params={"per_page": 5},
            )
            if response.status_code == 409:
                return []
            response.raise_for_status()
            return [
                {
                    "sha": item.get("sha", "")[:7],
                    "message": item.get("commit", {}).get("message", "").splitlines()[0],
                    "date": item.get("commit", {}).get("committer", {}).get("date"),
                    "url": item.get("html_url"),
                }
                for item in response.json()
            ]
        except Exception:
            return []
