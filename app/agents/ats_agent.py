from app.services.mistral_service import MistralService
from app.profile_context import build_profile_context
from app.utils import normalize_list, score_overlap


class ATSEvaluatorAgent:
    def __init__(self) -> None:
        self.llm = MistralService()

    async def evaluate(self, profile: dict, resume: dict, jd_analysis: dict, job_description: str | None = None) -> dict:
        candidate_terms = []
        for key in ("core_skills", "ats_keywords"):
            candidate_terms.extend(normalize_list(resume.get(key)))
        candidate_terms.extend(normalize_list(profile.get("skills")))

        target_terms = []
        for key in ("required_skills", "nice_to_have", "keywords"):
            target_terms.extend(normalize_list(jd_analysis.get(key)))

        overlap = score_overlap(candidate_terms, target_terms)
        score = min(98, max(35, int(overlap["ratio"] * 100)))
        missing = overlap["missing"][:12]

        fallback_feedback = [
            "Resume was ordered around the strongest verified evidence.",
            "ATS keywords were inserted only where supported by the candidate profile.",
        ]
        if missing:
            fallback_feedback.append("Missing skills are shown transparently rather than fabricated.")

        profile_context = build_profile_context(profile, max_projects=8, max_repos=8)
        prompt = f"""
Evaluate this tailored resume against the JD analysis as an ATS and senior technical recruiter.
Return strict JSON only.

Schema:
{{
  "score": 0,
  "matched_skills": ["specific matched skill/evidence"],
  "missing_skills": ["true missing or weakly evidenced requirement"],
  "feedback": ["3-6 concise actionable observations"],
  "keyword_coverage": "brief assessment",
  "truthfulness_risk": "low|medium|high",
  "recruiter_read": "one sentence explaining how a recruiter would perceive this resume"
}}

Rules:
- Score realistically. Do not inflate.
- Do not penalize missing skills that are clearly covered under equivalent wording.
- Missing skills must be requirements from the JD, not random words.

Job description: {job_description or ""}
JD analysis: {jd_analysis}
Resume: {resume}
Profile evidence: {profile_context}
"""
        llm_result = await self.llm.complete_json(
            prompt,
            system_prompt="You are a precise ATS evaluator and skeptical AI recruiter. Return only JSON.",
            temperature=0.1,
        )
        if llm_result:
            return {
                "score": int(llm_result.get("score") or score),
                "matched_skills": normalize_list(llm_result.get("matched_skills"))[:18] or overlap["matched"][:16],
                "missing_skills": normalize_list(llm_result.get("missing_skills"))[:12],
                "feedback": normalize_list(llm_result.get("feedback"))[:8] or fallback_feedback,
                "keyword_coverage": llm_result.get("keyword_coverage", ""),
                "truthfulness_risk": llm_result.get("truthfulness_risk", "low"),
                "recruiter_read": llm_result.get("recruiter_read", ""),
            }

        return {
            "score": score,
            "matched_skills": overlap["matched"][:16],
            "missing_skills": missing,
            "feedback": fallback_feedback,
        }
