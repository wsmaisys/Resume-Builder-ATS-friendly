from app.services.mistral_service import MistralService
from app.utils import extract_keywords, normalize_list


class JDAnalyzerAgent:
    def __init__(self) -> None:
        self.llm = MistralService()

    async def analyze(self, job_description: str) -> dict:
        prompt = f"""
Analyze this job description like a senior recruiter and ATS strategist.
Return strict JSON only. No markdown.

Schema:
{{
  "role_title": "best inferred role title",
  "company_context": "company/domain if inferable",
  "experience_level": "junior|mid|senior|lead|unknown",
  "role_summary": "2 sentence summary of what this job is really asking for",
  "must_have_skills": ["hard requirements only"],
  "nice_to_have": ["preferences"],
  "core_responsibilities": ["main responsibilities as recruiter would screen them"],
  "ats_keywords": ["exact ATS keyword phrases, normalized"],
  "business_outcomes": ["business outcomes the resume should speak to"],
  "risk_flags": ["requirements the candidate may not satisfy directly"],
  "resume_positioning": "one-sentence positioning strategy for Wasim",
  "keyword_groups": {{
    "agentic_ai": [],
    "backend_platform": [],
    "cloud_devops": [],
    "data_ml": [],
    "domain": []
  }}
}}

Rules:
- Keep skills as recruiter-facing phrases, not random single words.
- Separate true must-haves from nice-to-haves.
- Do not infer impossible facts.

Job description:
{job_description}
"""
        result = await self.llm.complete_json(
            prompt,
            system_prompt=(
                "You are an expert JD parser for ATS-optimized resume generation. "
                "You return only valid JSON and distinguish hard requirements from nice-to-have signals."
            ),
            temperature=0.1,
        )
        if not result:
            keywords = extract_keywords(job_description, limit=28)
            return {
                "role_title": "Not specified",
                "company_context": "Not specified",
                "must_have_skills": keywords[:12],
                "nice_to_have": keywords[12:20],
                "ats_keywords": keywords,
                "keywords": keywords,
                "experience_level": "Not specified",
                "role_summary": "Role inferred from the provided job description.",
                "core_responsibilities": [],
                "business_outcomes": [],
                "risk_flags": [],
                "resume_positioning": "Emphasize verified AI/ML, agentic AI, RAG, FastAPI, and deployment evidence.",
                "keyword_groups": {},
            }

        result["must_have_skills"] = normalize_list(result.get("must_have_skills") or result.get("required_skills"))
        result["required_skills"] = result["must_have_skills"]
        result["nice_to_have"] = normalize_list(result.get("nice_to_have"))
        result["ats_keywords"] = normalize_list(result.get("ats_keywords") or result.get("keywords"))
        result["keywords"] = result["ats_keywords"]
        result["core_responsibilities"] = normalize_list(result.get("core_responsibilities"))
        result["business_outcomes"] = normalize_list(result.get("business_outcomes"))
        result["risk_flags"] = normalize_list(result.get("risk_flags"))
        return result
