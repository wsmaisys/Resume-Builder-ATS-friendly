from app.services.mistral_service import MistralService
from app.utils import extract_keywords, normalize_list


class JDAnalyzerAgent:
    def __init__(self) -> None:
        self.llm = MistralService()

    async def analyze(self, job_description: str) -> dict:
        prompt = f"""
Analyze this job description for resume targeting.
Return strict JSON with keys:
required_skills, nice_to_have, keywords, experience_level, role_summary, domain_match.

Job description:
{job_description}
"""
        result = await self.llm.complete_json(prompt)
        if not result:
            keywords = extract_keywords(job_description, limit=28)
            return {
                "required_skills": keywords[:12],
                "nice_to_have": keywords[12:20],
                "keywords": keywords,
                "experience_level": "Not specified",
                "role_summary": "Role inferred from the provided job description.",
                "domain_match": "To be determined from matched candidate evidence.",
            }

        result["required_skills"] = normalize_list(result.get("required_skills"))
        result["nice_to_have"] = normalize_list(result.get("nice_to_have"))
        result["keywords"] = normalize_list(result.get("keywords"))
        return result

