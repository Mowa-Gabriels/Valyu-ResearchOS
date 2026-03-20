from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.team import Team
from agno.team.mode import TeamMode
from agno.models.google import Gemini
from agno.models.huggingface import HuggingFace


from agents import academic_agent, web_agent, paper_agent, domain_agent

db = SqliteDb(db_file="tmp/research_os.db")

research_team = Team(
    id="valyu-research-team",
    name="Valyu Research Team",
    mode=TeamMode.coordinate,
    model=HuggingFace(
        id="Qwen/Qwen2.5-Coder-32B-Instruct",
        max_tokens=4096,
    ),
    db=db,
    add_history_to_context=True,
    num_history_runs=5,
    members=[
        academic_agent,
        web_agent,
        paper_agent,
        domain_agent,
    ],
    description=(
        "A multi-agent research team that combines academic literature, "
        "live web content, deep paper analysis, and domain-scoped search "
        "to produce comprehensive, well-sourced research reports."
    ),
    instructions=[
        # ── delegation strategy ──────────────────────────────────────────
        "Break every research request into sub-tasks assigned to the best agent:",
        "  • academic-search-agent  → peer-reviewed literature & citations",
        "  • web-search-agent       → current news, blogs, official docs",
        "  • paper-deepdive-agent   → precise extraction from a known paper",
        "  • domain-scoped-agent    → when source credibility is critical",
        # ── coordination rules ───────────────────────────────────────────
        "Always start with academic-search-agent and web-search-agent in parallel.",
        "If a specific paper is surfaced, follow up with paper-deepdive-agent.",
        "For medical or life-science queries, always include domain-scoped-agent.",
        # ── synthesis rules ──────────────────────────────────────────────
        "Structure the final report as: Executive Summary → Academic Findings → "
        "Web Insights → Deep-Dive Details (if applicable) → Conclusion → Sources.",
        "Resolve contradictions between sources; note where consensus is lacking.",
        "Include a Sources section listing every URL / DOI used.",
    ],
    share_member_interactions=True,

    markdown=True,
)