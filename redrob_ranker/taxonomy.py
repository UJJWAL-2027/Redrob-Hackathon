"""Capability taxonomy derived from the official JD."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilitySpec:
    name: str
    weight: float
    phrases: tuple[str, ...]
    production_phrases: tuple[str, ...] = ()


PRODUCTION_PHRASES = (
    "production",
    "deployed",
    "launched",
    "shipped",
    "real users",
    "at scale",
    "scale",
    "latency",
    "monitoring",
    "on-call",
    "on call",
    "sla",
    "regression",
    "a/b",
    "ab test",
    "online experiment",
    "refresh",
    "pipeline",
    "owned",
    "maintained",
)

RESEARCH_ONLY_PHRASES = (
    "paper",
    "publication",
    "arxiv",
    "academic",
    "research-only",
    "research only",
    "thesis",
    "prototype",
    "proof of concept",
)

ASPIRATIONAL_AI_PHRASES = (
    "self-learner",
    "self learner",
    "online courses",
    "side project",
    "small rag",
    "played with",
    "haven't done it in a professional capacity",
    "not in a professional capacity",
    "interested in transitioning",
    "start contributing",
    "building competence",
    "learning modern ml",
)

CONSULTING_COMPANIES = {
    "accenture",
    "capgemini",
    "cognizant",
    "deloitte",
    "hcl",
    "ibm services",
    "infosys",
    "mindtree",
    "mphasis",
    "tata consultancy services",
    "tcs",
    "tech mahindra",
    "wipro",
}

NON_ENGINEERING_TITLES = (
    "marketing",
    "sales",
    "hr ",
    "human resources",
    "recruiter",
    "content writer",
    "graphic designer",
    "business analyst",
    "finance",
    "accountant",
    "project manager",
    "operations manager",
    "civil engineer",
    "mechanical engineer",
)

ENGINEERING_TITLES = (
    "ai engineer",
    "machine learning",
    "ml engineer",
    "data scientist",
    "software engineer",
    "backend engineer",
    "search engineer",
    "ranking engineer",
    "recommendation",
    "nlp engineer",
    "data engineer",
    "applied scientist",
    "staff engineer",
    "tech lead",
    "founding engineer",
)

CAPABILITIES: tuple[CapabilitySpec, ...] = (
    CapabilitySpec(
        "retrieval_systems",
        1.35,
        (
            "retrieval",
            "information retrieval",
            "semantic search",
            "hybrid search",
            "dense retrieval",
            "sparse retrieval",
            "bm25",
            "rag",
            "candidate search",
            "search relevance",
            "recommendation system",
            "recommender",
            "matching system",
        ),
        ("retrieval-quality", "index refresh", "embedding drift", "search latency"),
    ),
    CapabilitySpec(
        "vector_infrastructure",
        1.1,
        (
            "vector database",
            "vector search",
            "ann search",
            "approximate nearest",
            "faiss",
            "pinecone",
            "weaviate",
            "qdrant",
            "milvus",
            "elasticsearch",
            "opensearch",
            "hnsw",
            "embedding index",
        ),
    ),
    CapabilitySpec(
        "ranking_evaluation",
        1.3,
        (
            "ranking",
            "reranking",
            "learning to rank",
            "ltr",
            "ndcg",
            "mrr",
            "map",
            "offline evaluation",
            "evaluation framework",
            "ab testing",
            "a/b testing",
            "relevance judgment",
            "recruiter feedback",
        ),
    ),
    CapabilitySpec(
        "production_ml",
        1.15,
        (
            "ml pipeline",
            "model serving",
            "feature pipeline",
            "feature store",
            "inference",
            "mlops",
            "monitoring",
            "drift",
            "deployment",
            "production ml",
            "model registry",
            "batch inference",
        ),
    ),
    CapabilitySpec(
        "llm_systems",
        0.75,
        (
            "llm",
            "large language model",
            "fine-tuning",
            "fine tuning",
            "lora",
            "qlora",
            "peft",
            "prompt",
            "langchain",
            "agents",
            "openai",
            "transformers",
        ),
    ),
    CapabilitySpec(
        "python_backend",
        0.8,
        (
            "python",
            "fastapi",
            "django",
            "flask",
            "api",
            "backend",
            "microservice",
            "service",
            "sql",
            "postgres",
        ),
    ),
    CapabilitySpec(
        "product_engineering",
        0.85,
        (
            "product",
            "recruiter",
            "marketplace",
            "user engagement",
            "metrics",
            "pm",
            "feedback loop",
            "customer",
            "experiment",
            "growth",
        ),
    ),
    CapabilitySpec(
        "data_infrastructure",
        0.55,
        (
            "spark",
            "airflow",
            "kafka",
            "warehouse",
            "etl",
            "data pipeline",
            "streaming",
            "snowflake",
            "dbt",
            "feature engineering",
        ),
    ),
)

AI_SKILL_PHRASES = tuple(
    sorted({phrase for cap in CAPABILITIES[:5] for phrase in cap.phrases} | {"embedding", "embeddings", "nlp"})
)

TECH_RELEASE_YEAR = {
    "langchain": 2022,
    "pinecone": 2019,
    "qdrant": 2021,
    "milvus": 2019,
    "weaviate": 2019,
    "bge": 2023,
    "e5": 2022,
    "lora": 2021,
    "qlora": 2023,
    "chatgpt": 2022,
}

LOCATION_PREFERRED = (
    "pune",
    "noida",
    "delhi",
    "gurgaon",
    "gurugram",
    "ncr",
    "mumbai",
    "hyderabad",
    "bangalore",
    "bengaluru",
)
