import os

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.tools.valyu import ValyuTools
from agno.models.huggingface import HuggingFace
from dotenv import load_dotenv 

load_dotenv() 

db = SqliteDb(db_file="tmp/research_os.db")

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
_claude = lambda: Claude(id="claude-sonnet-4-6")
_huggingface = lambda: HuggingFace(
        id="meta-llama/Meta-Llama-3-8B-Instruct",
        max_tokens=4096,
    )

_key = VALYU_API_KEY

academic_agent = Agent(
    id="academic-search-agent",
    name="Academic Search Agent",
    role="Search peer-reviewed papers, journals, and academic publications",
    model=_huggingface(),
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
    instructions=[
        "Specialise in finding high-quality academic literature.",
        "Always include author, publication year, and DOI when available.",
        "Rank results by relevance score and highlight key findings.",
        "If no strong academic sources exist, say so explicitly.",
    ],
    tools=[ValyuTools(
        api_key=_key,
        enable_academic_search=True,
        enable_web_search=False,
        enable_paper_search=False,
        max_results=8,
        relevance_threshold=0.65,
        text_length=1500,
    )],
    markdown=True,
)

web_agent = Agent(
    id="web-search-agent",
    name="Web Search Agent",
    role="Search the open web for current information, news, and general content",
    model=_huggingface(),
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
    instructions=[
        "Specialise in finding current, up-to-date web content.",
        "Prioritise authoritative sources (.gov, .edu, official docs, reputable news).",
        "Note the recency of sources and flag anything older than 12 months.",
        "Avoid low-quality blogs or SEO-farm content.",
    ],
    tools=[ValyuTools(
        api_key=_key,
        enable_academic_search=False,
        enable_web_search=True,
        enable_paper_search=False,
        max_results=10,
        relevance_threshold=0.5,
        text_length=1200,
    )],
    markdown=True,
)

paper_agent = Agent(
    id="paper-deepdive-agent",
    name="Paper Deep-Dive Agent",
    role="Extract detailed methodology, results, and data from within specific papers",
    model=_huggingface(),
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
    instructions=[
        "Specialise in drilling into specific papers for precise details.",
        "Focus on methodology, datasets, results tables, and conclusions.",
        "Quote directly when precision matters; provide context where possible.",
        "Only activate when a specific paper or narrow technical question is raised.",
    ],
    tools=[ValyuTools(
        api_key=_key,
        enable_academic_search=False,
        enable_web_search=False,
        enable_paper_search=True,
        max_results=5,
        relevance_threshold=0.5,
        text_length=2000,
    )],
    markdown=True,
)

domain_agent = Agent(
    id="domain-scoped-agent",
    name="Domain-Scoped Search Agent",
    role="Search within a trusted allowlist of high-quality scientific domains",
    model=_huggingface(),
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
    instructions=[
        "Only search within pre-approved, high-quality domains.",
        "Return highly credible, domain-specific results.",
        "Clearly attribute every finding to its source domain.",
        "Use this agent when accuracy and source credibility are paramount.",
    ],
    tools=[ValyuTools(
        api_key=_key,
        enable_academic_search=False,
        enable_web_search=True,
        enable_paper_search=False,
        search_domains=[
            "nature.com",
            "pubmed.ncbi.nlm.nih.gov",
            "arxiv.org",
            "science.org",
            "thelancet.com",
        ],
        max_results=6,
        relevance_threshold=0.6,
        max_price=15.0,
    )],
    markdown=True,
)