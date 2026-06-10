from app.services.mistral_service import MistralService
from app.profile_context import build_profile_context


class CoverLetterAgent:
    def __init__(self) -> None:
        self.llm = MistralService()

    async def write(
        self,
        profile: dict,
        job_description: str,
        jd_analysis: dict,
        company_name: str | None = None,
        role_title: str | None = None,
    ) -> dict:
        plan = await self._plan(profile, job_description, jd_analysis, company_name, role_title)
        draft = await self._draft(profile, job_description, jd_analysis, plan, company_name, role_title)
        review = await self._review(draft, jd_analysis, plan)
        final = await self._revise(draft, review, company_name, role_title)
        if final:
            return self._sanitize(final, profile)
        if draft:
            return self._sanitize(draft, profile)

        role = role_title or "the role"
        company = company_name or "your team"
        return {
            "greeting": "Dear Hiring Team,",
            "paragraphs": [
                f"The {role} role at {company} aligns closely with my recent work building agentic AI, RAG, FastAPI, MCP, and cloud-deployed automation systems. I have focused on turning ambiguous workflows into working AI services that connect LLM reasoning with tools, APIs, retrieval layers, and production deployment constraints.",
                "My strongest evidence is practical. MediFlow combines multi-agent orchestration with patient-history tooling and a clinical RAG flow; the Nephrology RAG MCP Server exposes retrieval services through streamable HTTP; and DocuDroid applies LLM plus vector search for document QA. These projects map directly to agent workflows, RAG, API integration, and reliability requirements.",
                "I also bring useful domain range from legal documentation, retail operations, export logistics, and real estate consulting. That background helps me ask sharper workflow questions, identify automation bottlenecks, and design AI systems that are not just technically impressive but operationally usable.",
                "I would welcome the opportunity to discuss how my hands-on agentic AI portfolio, FastAPI deployment experience, and cross-domain automation background can support your work in building reliable AI automation for real business processes.",
            ],
            "closing": "Thank you for your consideration. I would welcome the opportunity to discuss how I can contribute.",
            "signature": profile.get("name", "Wasim Ansari"),
        }

    async def _plan(self, profile: dict, job_description: str, jd_analysis: dict, company_name: str | None, role_title: str | None) -> dict:
        profile_context = build_profile_context(profile, max_projects=5, max_repos=3)
        prompt = f"""
Create a cover letter strategy for this application.
Return strict JSON only.

Schema:
{{
  "opening_angle": "specific reason this candidate fits this role",
  "three_evidence_points": [
    {{"claim": "...", "proof": "specific project/experience/link/domain evidence"}}
  ],
  "company_alignment": "what to emphasize for this company/domain",
  "tone": "professional, direct, confident",
  "avoid": ["generic phrases or unsupported claims"]
}}

Company: {company_name or "Hiring Team"}
Role: {role_title or jd_analysis.get("role_title") or "the open role"}
JD analysis: {jd_analysis}
Job description: {job_description}
Profile compact evidence: {profile_context}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt="You are a senior application strategist. Return only JSON.",
            temperature=0.15,
        ) or {}

    async def _draft(self, profile: dict, job_description: str, jd_analysis: dict, plan: dict, company_name: str | None, role_title: str | None) -> dict:
        profile_context = build_profile_context(profile, max_projects=5, max_repos=3)
        prompt = f"""
Write a polished one-page cover letter JSON from the strategy.
Return strict JSON only.

Schema:
{{
  "greeting": "Dear Hiring Team,",
  "paragraphs": ["paragraph 1", "paragraph 2", "paragraph 3", "paragraph 4"],
  "closing": "closing sentence",
  "signature": "Wasim Ansari"
}}

Requirements:
- 4 paragraphs, each 45-75 words.
- The first paragraph must name the role/company and a specific fit.
- Include 2-3 concrete project/experience proof points from profile.
- No generic filler, no exaggerated claims, no unsupported metrics.
- Sound like a serious AI/automation engineer, not a template.
- Do not use "I am excited to apply" or other template openings.
- Do not invent metrics, dates, client names, or employer claims.

Company: {company_name or "Hiring Team"}
Role: {role_title or jd_analysis.get("role_title") or "the open role"}
Strategy: {plan}
JD analysis: {jd_analysis}
Job description: {job_description}
Profile compact evidence: {profile_context}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt="You are an expert technical cover letter writer for AI/ML and automation roles. Return only JSON.",
            temperature=0.3,
        ) or {}

    async def _review(self, draft: dict, jd_analysis: dict, plan: dict) -> dict:
        if not draft:
            return {}
        prompt = f"""
Critique this cover letter for specificity, credibility, role alignment, and recruiter impact.
Return strict JSON only.

Schema:
{{
  "score": 0,
  "issues": ["specific issue"],
  "generic_phrases": ["phrase"],
  "missing_evidence": ["evidence needed"],
  "revision_instructions": ["specific edit"]
}}

JD analysis: {jd_analysis}
Strategy: {plan}
Draft: {draft}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt="You are a skeptical hiring manager reviewing an AI role cover letter. Return only JSON.",
            temperature=0.1,
        ) or {}

    async def _revise(self, draft: dict, review: dict, company_name: str | None, role_title: str | None) -> dict:
        if not draft:
            return {}
        prompt = f"""
Revise this cover letter using the critique.
Return final JSON with keys greeting, paragraphs, closing, signature.

Rules:
- Fix generic language.
- Keep 4 paragraphs.
- Preserve truthfulness.
- Remove "I am excited to apply" and similar template openings.
- Make it specific to {role_title or "the role"} at {company_name or "the company"}.
- No markdown.

Critique: {review}
Draft: {draft}
"""
        return await self.llm.complete_json(
            prompt,
            system_prompt="You are a final-pass cover letter editor. Return only JSON.",
            temperature=0.2,
        ) or {}

    def _sanitize(self, letter: dict, profile: dict) -> dict:
        letter.setdefault("greeting", "Dear Hiring Team,")
        paragraphs = letter.get("paragraphs", [])
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]
        letter["paragraphs"] = [self._clean_paragraph(str(p).strip()) for p in paragraphs if str(p).strip()][:4]
        letter.setdefault("closing", "Thank you for your consideration. I would welcome the opportunity to discuss how I can contribute.")
        if letter["paragraphs"] and "welcome the opportunity" in letter["paragraphs"][-1].lower():
            letter["closing"] = "Sincerely,"
        letter.setdefault("signature", profile.get("name", "Wasim Ansari"))
        return letter

    def _clean_paragraph(self, paragraph: str) -> str:
        replacements = {
            "full observability and guardrails": "observability and guardrail considerations",
            "AWS EC2, ": "",
            "strict SLA requirements": "delivery requirements",
            "5+ client engagements": "multiple client engagements",
            "I am excited to apply": "I am applying",
        }
        value = paragraph
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
