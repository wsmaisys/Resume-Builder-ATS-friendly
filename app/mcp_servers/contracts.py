from typing import Any


def ok_response(data: dict[str, Any], usage_guidance: str) -> dict[str, Any]:
    return {
        "ok": True,
        "error": None,
        "usage_guidance": usage_guidance,
        "data": data,
    }


def error_response(message: str, usage_guidance: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "message": message,
            "details": details or {},
        },
        "usage_guidance": usage_guidance,
        "data": {},
    }


def compact_repo(repo: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": repo.get("name"),
        "repo_url": repo.get("url"),
        "description": repo.get("description"),
        "primary_language": repo.get("language"),
        "stars": repo.get("stars"),
        "forks": repo.get("forks"),
        "topics": repo.get("topics", []),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "deployed_urls": repo.get("deployed_urls", []),
        "artifact_urls": repo.get("artifact_urls", []),
        "recent_commits": repo.get("recent_commits", []),
    }
