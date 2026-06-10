import json
from copy import deepcopy

from app.config import DATA_DIR


DEFAULT_PROFILE = {
    "name": "Wasim Ansari",
    "title": "AI/ML Engineer",
    "contact": {
        "portfolio": "https://wsmaisys.github.io/waseemmansari.github.io/",
        "github": "https://github.com/wsmaisys",
    },
    "skills": [
        "GenAI engineering",
        "Agentic AI",
        "RAG",
        "LangGraph",
        "CrewAI",
        "Mistral",
        "FastAPI",
        "Python",
        "Neo4j",
        "MLOps",
        "Cloud deployments",
        "Docker",
        "BeautifulSoup",
        "GitHub API",
        "Document generation",
        "Business automation",
        "Legal domain analysis",
    ],
    "experience": [
        {
            "role": "AI/ML and GenAI Builder",
            "organization": "Independent projects and portfolio work",
            "highlights": [
                "Builds LLM-powered applications with agentic workflows, RAG, and Python APIs.",
                "Designs practical AI tools that connect business goals with production-oriented implementation.",
                "Works across legal, entrepreneurial, and technical contexts.",
            ],
        }
    ],
    "projects": [
        {
            "name": "AI Resume Builder",
            "summary": "FastAPI application for ATS-aware resume and cover letter generation using Mistral, profile enrichment, and PDF rendering.",
            "skills": ["FastAPI", "Mistral", "WeasyPrint", "BeautifulSoup", "GitHub API"],
        },
        {
            "name": "Agentic AI and RAG Systems",
            "summary": "Portfolio work involving retrieval-augmented generation, orchestration, and AI workflow design.",
            "skills": ["RAG", "LangGraph", "CrewAI", "Neo4j", "Python"],
        },
    ],
    "education": [
        {
            "program": "Diploma in Data Science",
            "institution": "IIT Madras",
            "notes": "Mentioned in the project plan as part of the complete profile.",
        },
        {
            "program": "Legal background",
            "institution": "Profile context",
            "notes": "Legal and business experience included as transferable domain strength.",
        },
    ],
    "certifications": [],
}


class ProfileStore:
    def __init__(self) -> None:
        DATA_DIR.mkdir(exist_ok=True)
        self.path = DATA_DIR / "master_profile.json"

    def load(self) -> dict:
        if not self.path.exists():
            self.save(DEFAULT_PROFILE)
            return deepcopy(DEFAULT_PROFILE)
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.save(DEFAULT_PROFILE)
            return deepcopy(DEFAULT_PROFILE)

    def save(self, profile: dict) -> None:
        self.path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

