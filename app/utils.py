import re
from collections import Counter


STOPWORDS = {
    "and", "the", "for", "with", "you", "our", "are", "will", "this", "that",
    "from", "have", "has", "your", "role", "team", "work", "job", "skills",
    "experience", "candidate", "using", "build", "develop", "ability",
    "hiring", "preferred", "required", "responsibilities", "requirements",
    "looking", "strong", "excellent", "systems", "services",
}

KNOWN_TERMS = [
    "retrieval augmented generation",
    "production ml",
    "cloud deployment",
    "document workflows",
    "github integrations",
    "llm agents",
    "fastapi",
    "langgraph",
    "crewai",
    "mistral",
    "python",
    "dockerized deployments",
    "docker",
    "github",
    "rag",
    "ats",
    "mlops",
    "neo4j",
    "kubernetes",
    "terraform",
    "beautifulsoup",
]


def normalize_term(value: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]", "", value.lower()).strip()


def normalize_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        value = [value]
    return [str(item).strip() for item in value if str(item).strip()]


def extract_keywords(text: str, limit: int = 24) -> list[str]:
    lowered = text.lower()
    terms = []
    for term in KNOWN_TERMS:
        if term in lowered:
            terms.append(_display_term(term))

    words = [word.strip(".,:;()[]{}") for word in re.findall(r"[A-Za-z][A-Za-z0-9+#.]{2,}", text)]
    normalized = [
        word for word in words
        if word.lower() not in STOPWORDS and normalize_term(word) not in {normalize_term(term) for term in terms}
    ]
    counts = Counter(normalized)
    return (terms + [word for word, _ in counts.most_common(limit)])[:limit]


def _display_term(term: str) -> str:
    special = {
        "fastapi": "FastAPI",
        "langgraph": "LangGraph",
        "crewai": "CrewAI",
        "mistral": "Mistral",
        "python": "Python",
        "docker": "Docker",
        "github": "GitHub",
        "rag": "RAG",
        "ats": "ATS",
        "mlops": "MLOps",
        "neo4j": "Neo4j",
        "beautifulsoup": "BeautifulSoup",
        "llm agents": "LLM agents",
        "production ml": "Production ML",
    }
    return special.get(term, term.title())


def score_overlap(candidate_terms: list[str], target_terms: list[str]) -> dict:
    candidate_map = {normalize_term(term): term for term in candidate_terms if normalize_term(term)}
    target_map = {normalize_term(term): term for term in target_terms if normalize_term(term)}
    matched = []
    missing = []

    for target_key, target_original in target_map.items():
        if any(target_key in candidate_key or candidate_key in target_key for candidate_key in candidate_map):
            matched.append(target_original)
        else:
            missing.append(target_original)

    ratio = len(matched) / max(1, len(target_map))
    return {"matched": matched, "missing": missing, "ratio": ratio}
