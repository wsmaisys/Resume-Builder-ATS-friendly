import re

from app.services.mistral_service import MistralService
from app.profile_context import build_profile_context
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
        evidence = await self._select_evidence(profile, job_description, jd_analysis, role_title)
        draft = await self._draft_resume(profile, job_description, jd_analysis, evidence, role_title)
        review = await self._review_resume(draft, jd_analysis, evidence)
        final = await self._revise_resume(draft, review, jd_analysis, evidence)
        if final:
            return self._sanitize_resume(final, profile, role_title)
        if draft:
            return self._sanitize_resume(draft, profile, role_title)

        required = jd_analysis.get("required_skills", []) + jd_analysis.get("keywords", [])
        skills = profile.get("skills", [])
        matched = score_overlap(skills, required)["matched"]
        return self._sanitize_resume({
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
        }, profile, role_title)

    async def _select_evidence(self, profile: dict, job_description: str, jd_analysis: dict, role_title: str | None) -> dict:
        profile_context = build_profile_context(profile, max_projects=10, max_repos=8)
        prompt = f"""
Select only the strongest truthful candidate evidence for this role.
Return strict JSON only.

Schema:
{{
  "target_headline": "role-aligned headline, max 12 words, no unsupported seniority",
  "positioning": "sharp recruiter-facing positioning, max 35 words",
  "top_skills": ["12-18 skills that best match the JD"],
  "experience_strategy": [
    {{"role": "...", "organization": "...", "why_relevant": "...", "priority": 1}}
  ],
  "project_strategy": [
    {{"name": "...", "why_relevant": "...", "proof_links": ["repo/deployed links if present"], "priority": 1}}
  ],
  "gap_strategy": ["how to handle missing requirements without fabrication"],
  "do_not_claim": ["skills or experience that must not be claimed"]
}}

Selection rules:
- Choose at most 3 experience entries.
- Choose at most 5 projects.
- Prefer deployed projects and GitHub-backed projects.
- Prioritize evidence that directly maps to must-have skills and responsibilities.
- Never include a project merely because it exists.
- Do not introduce years of experience beyond what the profile explicitly says.

Target role: {role_title or jd_analysis.get("role_title") or "Not specified"}
JD analysis: {jd_analysis}
Job description: {job_description}
Master profile compact evidence: {profile_context}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt=(
                "You are a rigorous resume evidence selector. You optimize relevance, proof, and truthfulness. "
                "Return only JSON."
            ),
            temperature=0.15,
        ) or {}

    async def _draft_resume(
        self,
        profile: dict,
        job_description: str,
        jd_analysis: dict,
        evidence: dict,
        role_title: str | None,
    ) -> dict:
        profile_context = build_profile_context(profile, max_projects=10, max_repos=8)
        prompt = f"""
Write a polished ATS-friendly resume JSON using only selected evidence and master profile facts.
Return strict JSON only.

Schema:
{{
  "candidate_name": "Wasim Ansari",
  "headline": "targeted headline",
  "contact": {{"email": "...", "phone": "...", "location": "...", "portfolio": "...", "github": "...", "linkedin": "..."}},
  "summary": "3 compact lines, specific to the target role, no fluff",
  "core_skills": ["18-24 role-matched skills grouped naturally"],
  "selected_experience": [
    {{
      "role": "...",
      "organization": "...",
      "location": "...",
      "period": "...",
      "highlights": ["3-5 accomplishment bullets, each 16-28 words, ATS keywords used naturally"]
    }}
  ],
  "selected_projects": [
    {{
      "name": "...",
      "summary": "1 strong outcome-oriented sentence",
      "skills": ["5-8 relevant technologies"],
      "repo_url": "...",
      "deployed_urls": ["..."],
      "highlights": ["1-2 bullets showing relevance"]
    }}
  ],
  "education": [],
  "certifications": [],
  "ats_keywords": [],
  "truthfulness_notes": []
}}

Quality bar:
- This must look like a serious senior AI/automation resume, not a generic LLM bio.
- Resume should fit 1-2 pages: max 3 experience entries, max 5 projects.
- Lead with the strongest match to the JD.
- Rewrite bullets for relevance, but never invent employers, dates, credentials, links, or metrics.
- Do not invent percentages, time savings, revenue impact, client names, or unsupported seniority.
- Preserve exact employment periods from the profile.
- If the target title says architect/senior, align positioning through project evidence rather than unsupported title inflation.
- Use exact deployed/repo links when present in profile.
- Avoid weak phrases like "excited", "passionate", "business-facing product thinking", or "useful range".

Target role: {role_title or jd_analysis.get("role_title") or "Not specified"}
JD analysis: {jd_analysis}
Evidence strategy: {evidence}
Job description: {job_description}
Master profile compact evidence: {profile_context}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt=(
                "You are an elite technical resume writer for AI/ML, agentic AI, automation, and platform roles. "
                "You write concise, evidence-backed, recruiter-grade resume JSON. Return only JSON."
            ),
            temperature=0.25,
        ) or {}

    async def _review_resume(self, draft: dict, jd_analysis: dict, evidence: dict) -> dict:
        if not draft:
            return {}
        prompt = f"""
Critique this resume draft against the JD analysis and evidence strategy.
Return strict JSON only.

Schema:
{{
  "score": 0,
  "major_issues": ["specific issue"],
  "missing_keywords": ["keyword"],
  "overclaim_risks": ["claim that may be unsupported"],
  "weak_bullets": ["quote or describe weak bullet"],
  "revision_instructions": ["specific edit instruction"],
  "keep": ["strong elements to preserve"]
}}

Scoring rubric:
- 90+ means highly targeted, credible, concise, role-aligned, and ATS strong.
- Penalize generic summaries, too many projects, weak verbs, unsupported claims, and missing must-have terms.

JD analysis: {jd_analysis}
Evidence strategy: {evidence}
Resume draft: {draft}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt="You are a skeptical ATS evaluator and senior recruiter. Return only JSON.",
            temperature=0.1,
        ) or {}

    async def _revise_resume(self, draft: dict, review: dict, jd_analysis: dict, evidence: dict) -> dict:
        if not draft:
            return {}
        prompt = f"""
Revise the resume draft using the critique. Return the final resume JSON only.

Keep the same schema as the draft. Requirements:
- Fix every major issue that can be fixed truthfully.
- Add missing ATS keywords only where supported by evidence.
- Remove weak/generic language.
- Keep max 3 experience entries and max 5 projects.
- Preserve exact links and dates from the draft/profile.
- Remove invented metrics and unsupported years of experience.
- Make the final document polished enough for a real application.

JD analysis: {jd_analysis}
Evidence strategy: {evidence}
Critique: {review}
Draft resume: {draft}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt="You are a final-pass executive resume editor. Return only valid JSON.",
            temperature=0.15,
        ) or {}

    def _sanitize_resume(self, resume: dict, profile: dict, role_title: str | None) -> dict:
        experience_by_key = {
            (str(exp.get("role", "")).lower(), str(exp.get("organization", "")).lower()): exp
            for exp in profile.get("experience", [])
        }
        experience_by_role = {
            str(exp.get("role", "")).lower(): exp
            for exp in profile.get("experience", [])
        }
        contact = profile.get("contact", {})
        resume.setdefault("candidate_name", profile.get("name", "Wasim Ansari"))
        resume.setdefault("headline", role_title or profile.get("title", "AI/ML Engineer"))
        if "senior" not in str(role_title or "").lower():
            resume["headline"] = re.sub(r"^Senior\s+", "", str(resume["headline"]), flags=re.I)
            if resume.get("summary"):
                resume["summary"] = re.sub(r"\bSenior AI engineer\b", "AI engineer", str(resume["summary"]), flags=re.I)
                resume["summary"] = re.sub(r"\bSenior AI/ML engineer\b", "AI/ML engineer", str(resume["summary"]), flags=re.I)
        resume.setdefault("contact", contact)
        if not isinstance(resume.get("contact"), dict):
            resume["contact"] = contact
        for key in ("email", "phone", "location", "portfolio", "github", "linkedin"):
            if contact.get(key) and not resume["contact"].get(key):
                resume["contact"][key] = contact[key]

        resume["core_skills"] = list(dict.fromkeys(resume.get("core_skills", [])))[:24]
        resume["selected_experience"] = resume.get("selected_experience", [])[:3]
        for exp in resume["selected_experience"]:
            key = (str(exp.get("role", "")).lower(), str(exp.get("organization", "")).lower())
            source = experience_by_key.get(key) or experience_by_role.get(str(exp.get("role", "")).lower())
            if source:
                exp["period"] = source.get("period")
                exp["location"] = source.get("location")
                exp["organization"] = source.get("organization", exp.get("organization"))
            exp["highlights"] = [self._remove_unsupported_metric(point) for point in exp.get("highlights", [])[:5]]
        resume["selected_projects"] = resume.get("selected_projects", [])[:5]
        for project in resume["selected_projects"]:
            project["skills"] = project.get("skills", [])[:8]
            project["highlights"] = project.get("highlights", [])[:2]
            project["deployed_urls"] = project.get("deployed_urls", [])[:2]
        resume["education"] = resume.get("education", profile.get("education", []))[:2]
        resume["certifications"] = resume.get("certifications", profile.get("certifications", []))[:4]
        resume["ats_keywords"] = list(dict.fromkeys(resume.get("ats_keywords", [])))[:30]
        resume.setdefault("truthfulness_notes", ["Generated from verified profile, GitHub, portfolio, and CV facts."])
        return resume

    def _remove_unsupported_metric(self, text: str) -> str:
        value = str(text)
        replacements = {
            "reducing manual review time by 40%": "improving operational review efficiency",
            "reducing processing errors by 30%": "improving document review consistency",
            "improving cross-functional engineering collaboration and reducing processing errors by 30%": "supporting cross-functional engineering collaboration and document review consistency",
            "AWS EC2, ": "",
            "under strict SLA requirements": "within delivery timelines",
            "5+ client engagements": "multiple client engagements",
            "high-volumeconcurrent": "high-volume concurrent",
            "production-focusedin": "in",
        }
        for old, new in replacements.items():
            value = value.replace(old, new)
        value = re.sub(r"\b\d+(?:\.\d+)?%\s*(?:uptime|reduction|increase|improvement|accuracy)?", "production-focused", value, flags=re.I)
        value = re.sub(r"\b\d+K\+\s*(?:daily\s+)?(?:queries|documents/month|documents|users)?", "high-volume", value, flags=re.I)
        value = re.sub(r"reducing [^.]+ by production-focused", "improving operational workflow efficiency", value, flags=re.I)
        value = re.sub(r"reduced [^.]+ by production-focused", "improved operational workflow efficiency", value, flags=re.I)
        value = re.sub(r"\s{2,}", " ", value).strip()
        value = value.replace(" ,", ",")
        value = value.rstrip(",")
        return value
