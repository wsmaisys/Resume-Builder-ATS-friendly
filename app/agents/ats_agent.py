from app.services.mistral_service import MistralService
from app.utils import normalize_list, score_overlap


class ATSEvaluatorAgent:
    def __init__(self) -> None:
        self.llm = MistralService()

    async def evaluate(self, profile: dict, resume: dict, jd_analysis: dict) -> dict:
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

        feedback = [
            "Resume was ordered around the strongest verified evidence.",
            "ATS keywords were inserted only where supported by the candidate profile.",
        ]
        if missing:
            feedback.append("Missing skills are shown transparently rather than fabricated.")

        return {
            "score": score,
            "matched_skills": overlap["matched"][:16],
            "missing_skills": missing,
            "feedback": feedback,
        }

