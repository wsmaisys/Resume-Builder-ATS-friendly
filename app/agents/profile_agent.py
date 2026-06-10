from app.config import get_settings
from app.services.github_service import GitHubService
from app.services.mistral_service import MistralService
from app.services.portfolio_service import PortfolioService
from app.services.profile_store import ProfileStore


class ProfileAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.store = ProfileStore()
        self.llm = MistralService()
        self.github = GitHubService()
        self.portfolio = PortfolioService()

    async def refresh_profile(self) -> dict:
        base_profile = self.store.load()
        github_data = await self.github.fetch_profile(self.settings.github_username)
        portfolio_data = await self.portfolio.fetch(self.settings.portfolio_url)

        prompt = f"""
Create a truthful MasterCandidateProfile JSON by merging the existing profile,
portfolio text, and GitHub signals. Never invent employers, dates, degrees, or skills.
Keep concise but recruiter-useful evidence.

Existing profile:
{base_profile}

Portfolio:
{portfolio_data}

GitHub:
{github_data}
"""
        enriched = await self.llm.complete_json(prompt)
        if enriched:
            base_profile.update(enriched)
        base_profile["sources"] = {
            "portfolio": portfolio_data,
            "github": github_data,
        }
        self.store.save(base_profile)
        return base_profile

