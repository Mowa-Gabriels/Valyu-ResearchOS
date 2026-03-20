"""
Valyu Research OS — AgentOS + FastAPI service
pip install agno valyu fastapi uvicorn python-dotenv
"""

from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agno.os import AgentOS

from agents import academic_agent, web_agent, paper_agent, domain_agent
from team import research_team

load_dotenv()


# ── 1. Custom FastAPI app (your own routes live here) ─────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Valyu Research OS starting…")
    yield
    print("🛑 Valyu Research OS shutting down…")

app = FastAPI(
    title="Valyu Research OS",
    description="Multi-agent research service powered by Agno + ValyuTools",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health & meta routes ──────────────────────────────────────────────────────
@app.get("/status")
async def status():
    return {
        "status": "ok",
        "service": "valyu-research-os",
        "agents": 4,
        "team": "valyu-research-team",
        "db": "tmp/research_os.db",
    }

@app.get("/agents/list")
async def list_agents():
    return {
        "agents": [
            {"id": "academic-search-agent",  "role": "Academic literature search"},
            {"id": "web-search-agent",        "role": "General web search"},
            {"id": "paper-deepdive-agent",    "role": "Deep paper extraction"},
            {"id": "domain-scoped-agent",     "role": "Trusted-domain search"},
        ]
    }

@app.get("/teams/list")
async def list_teams():
    return {
        "teams": [
            {"id": "valyu-research-team", "mode": "coordinate", "members": 4}
        ]
    }


# ── 2. AgentOS — wraps custom app, auto-registers all agent/team endpoints ────
agent_os = AgentOS(
    name="Valyu Research OS",
    description="Production research service with 4 specialised Valyu agents",
    agents=[academic_agent, web_agent, paper_agent, domain_agent],
    teams=[research_team],
    base_app=app,       # mount AgentOS routes onto our custom FastAPI app
    tracing=True,       # enable session tracing in AgentOS control plane
)

# Final combined app (AgentOS merges its routes with ours)
app = agent_os.get_app()


# ── 3. Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    agent_os.serve(
        app="app:app",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )