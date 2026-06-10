def build_profile_context(profile: dict, max_projects: int = 12, max_repos: int = 12) -> dict:
    projects = []
    for project in profile.get("projects", [])[:max_projects]:
        projects.append(
            {
                "name": project.get("name"),
                "summary": project.get("summary"),
                "skills": project.get("skills", []),
                "repo_url": project.get("repo_url"),
                "deployed_urls": project.get("deployed_urls", []),
                "artifact_urls": project.get("artifact_urls", []),
                "github_updated_at": project.get("github_updated_at"),
            }
        )

    repos = []
    for repo in profile.get("github_repositories", [])[:max_repos]:
        repos.append(
            {
                "name": repo.get("name"),
                "repo_url": repo.get("repo_url"),
                "description": repo.get("description"),
                "primary_language": repo.get("primary_language"),
                "updated_at": repo.get("updated_at"),
                "deployed_urls": repo.get("deployed_urls", []),
                "artifact_urls": repo.get("artifact_urls", []),
                "recent_commits": repo.get("recent_commits", [])[:2],
            }
        )

    return {
        "name": profile.get("name"),
        "title": profile.get("title"),
        "contact": profile.get("contact", {}),
        "summary": profile.get("summary"),
        "skills": profile.get("skills", [])[:80],
        "experience": profile.get("experience", [])[:7],
        "projects": projects,
        "education": profile.get("education", []),
        "certifications": profile.get("certifications", []),
        "languages": profile.get("languages", []),
        "publications": profile.get("publications", []),
        "external_profiles": profile.get("external_profiles", {}),
        "github_repositories": repos,
    }
