from app.services.mistral_service import MistralService
from app.utils import score_overlap


class ResumeStrategistAgent:
    def __init__(self) -> None:
        self.llm = MistralService()

    async def build_resume(
        self,
        profile: dict,
        job_description: str,
        jd_analysis: dict,
        role_title: str | None = None,
    ) -> dict:
        prompt = f"""
You are a resume strategist. Build a truthful ATS-optimized resume JSON.
Rules:
- Never invent skills, employers, projects, degrees, dates, links, or metrics.
- Reorder projects and experience by relevance to the JD.
- Highlight transferable skills where direct match does not exist.
- Keep it recruiter-friendly and concise.

Return strict JSON with keys:
candidate_name, headline, contact, summary, core_skills, selected_experience,
selected_projects, education, certifications, ats_keywords, truthfulness_notes.

Target role: {role_title or "Not specified"}
JD analysis: {jd_analysis}
Job description: {job_description}
Master profile: {profile}
"""
        result = await self.llm.complete_json(prompt)
        if result:
            return result

        required = jd_analysis.get("required_skills", []) + jd_analysis.get("keywords", [])
        skills = profile.get("skills", [])
        matched = score_overlap(skills, required)["matched"]
        return {
            "candidate_name": profile.get("name", "Wasim Ansari"),
            "headline": role_title or profile.get("title", "AI/ML Engineer"),
            "contact": profile.get("contact", {}),
            "summary": (
                "AI/ML engineer focused on agentic AI, RAG systems, FastAPI services, "
                "MLOps workflows, and business-focused automation."
            ),
            "core_skills": matched + [skill for skill in skills if skill not in matched][:16],
            "selected_experience": profile.get("experience", []),
            "selected_projects": profile.get("projects", []),
            "education": profile.get("education", []),
            "certifications": profile.get("certifications", []),
            "ats_keywords": required[:24],
            "truthfulness_notes": [
                "Fallback mode used cached profile facts only.",
                "No unverifiable claims were added.",
            ],
        }

