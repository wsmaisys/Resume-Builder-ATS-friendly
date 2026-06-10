from app.services.mistral_service import MistralService


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
        prompt = f"""
Write a one-page professional, tailored cover letter.
Avoid generic filler. Be specific, truthful, and aligned to the job description.
Return strict JSON with keys: greeting, paragraphs, closing, signature.

Company: {company_name or "Hiring Team"}
Role: {role_title or "the open role"}
JD analysis: {jd_analysis}
Job description: {job_description}
Profile: {profile}
"""
        result = await self.llm.complete_json(prompt)
        if result:
            return result

        role = role_title or "the role"
        company = company_name or "your team"
        return {
            "greeting": "Dear Hiring Team,",
            "paragraphs": [
                f"I am excited to apply for {role} at {company}. My background combines AI/ML engineering, agentic workflows, RAG systems, FastAPI applications, and business-facing product thinking.",
                "I have built projects around LLM orchestration, retrieval systems, MLOps, and cloud-ready Python services, and I approach resume-level claims with the same discipline I bring to production AI systems: clear evidence, truthful scope, and measurable alignment.",
                "The role appears to need someone who can connect modern AI tooling with practical delivery. That is the space where my technical, legal, and entrepreneurial background gives me useful range.",
            ],
            "closing": "Thank you for your consideration. I would welcome the opportunity to discuss how I can contribute.",
            "signature": profile.get("name", "Wasim Ansari"),
        }

