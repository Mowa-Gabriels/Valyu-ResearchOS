"""
Valyu Research OS — Redesigned Agentic Interface
pip install streamlit requests
Run: streamlit run valyu_ui.py
"""

import json
import time
import uuid
import hashlib
import requests
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:7777"
TEAM_ID  = "valyu-research-team"

AGENT_IDS = [
    "academic-search-agent",
    "web-search-agent",
    "paper-deepdive-agent",
    "domain-scoped-agent",
]

AGENT_META = {
    "academic-search-agent": {
        "label":       "Academic Search",
        "short":       "ACAD",
        "icon":        "◈",
        "color":       "#00FFB3",
        "description": "Peer-reviewed databases, arXiv, Semantic Scholar",
        "tasks":       ["Querying arXiv", "Scanning Semantic Scholar", "Fetching citations"],
    },
    "web-search-agent": {
        "label":       "Web Search",
        "short":       "WEB",
        "icon":        "◎",
        "color":       "#4D9EFF",
        "description": "Live web, news feeds, and technical blogs",
        "tasks":       ["Crawling web sources", "Parsing news feeds", "Extracting key data"],
    },
    "paper-deepdive-agent": {
        "label":       "Paper Deep Dive",
        "short":       "DEEP",
        "icon":        "◐",
        "color":       "#FFB830",
        "description": "Full-text paper analysis and synthesis",
        "tasks":       ["Reading full papers", "Extracting methodology", "Synthesising findings"],
    },
    "domain-scoped-agent": {
        "label":       "Trusted Sources",
        "short":       "TRUST",
        "icon":        "◉",
        "color":       "#C77DFF",
        "description": "Curated domain-specific knowledge bases",
        "tasks":       ["Consulting domain KB", "Cross-referencing facts", "Verifying claims"],
    },
}

MODE_LABELS = ["◈  Full Team", "◈  Academic", "◎  Web Search", "◐  Deep Dive", "◉  Trusted"]
MODE_VALUES = ["team"] + AGENT_IDS
MODE_BY_LABEL = dict(zip(MODE_LABELS, MODE_VALUES))
LABEL_BY_MODE = dict(zip(MODE_VALUES, MODE_LABELS))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Valyu · Research OS",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Syne:wght@700;800&display=swap');

:root {
  --bg:     #080a0f;
  --bg1:    #0c0f16;
  --bg2:    #111520;
  --bg3:    #161b28;
  --border: #1c2233;
  --brd2:   #232b3e;
  --text:   #6b7a96;
  --text2:  #b0bdd0;
  --text3:  #e4eaf3;
  --teal:   #00FFB3;
  --blue:   #4D9EFF;
  --amber:  #FFB830;
  --purple: #C77DFF;
  --red:    #FF5B6A;
  --dim:    rgba(0,255,179,0.05);
  --mono:   'IBM Plex Mono', monospace;
  --disp:   'Syne', sans-serif;
}

html, body, [class*="css"], .stApp {
  font-family: var(--mono) !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
section[data-testid="stSidebar"] { display: none !important; }

.block-container {
  padding: 0 28px 32px 28px !important;
  max-width: 100% !important;
}

/* ── top bar ── */
.vr-topbar {
  display: flex; align-items: center;
  padding: 0 4px; height: 52px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px; gap: 20px;
  position: relative;
}
.vr-topbar::after {
  content: ''; position: absolute;
  bottom: -1px; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,255,179,0.4) 40%, rgba(77,158,255,0.3) 70%, transparent);
}
.vr-logo {
  font-family: var(--disp); font-size: 14px; font-weight: 800;
  color: var(--text3); letter-spacing: 0.06em;
  display: flex; align-items: center; gap: 9px; flex-shrink: 0;
}
.vr-logo-mark {
  width: 26px; height: 26px; border: 1.5px solid var(--teal);
  border-radius: 5px; display: flex; align-items: center;
  justify-content: center; color: var(--teal); font-size: 13px;
}
.spacer { flex: 1; }
.vr-stat { display: flex; flex-direction: column; align-items: flex-end; }
.vr-stat-v { font-size: 13px; font-weight: 500; color: var(--text3); line-height: 1; }
.vr-stat-l { font-size: 9px; color: var(--text); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 2px; }
.vr-sep { width: 1px; height: 26px; background: var(--border); }
.srv-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--red); display: inline-block; margin-right: 6px; }
.srv-dot.live { background: var(--teal); animation: pdot 2s ease-in-out infinite; }
@keyframes pdot { 0%,100% { box-shadow: 0 0 0 0 rgba(0,255,179,0.6); } 50% { box-shadow: 0 0 0 4px rgba(0,255,179,0); } }

/* ── route radio ── */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div { flex-direction: column !important; gap: 5px !important; }
div[data-testid="stRadio"] > div > label {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 5px !important;
  padding: 8px 12px !important;
  margin: 0 !important;
  cursor: pointer !important;
  width: 100% !important;
  transition: border-color 0.2s, background 0.2s !important;
}
div[data-testid="stRadio"] > div > label:hover { border-color: var(--brd2) !important; }
div[data-testid="stRadio"] > div > label:has(input:checked) {
  border-color: var(--teal) !important;
  background: var(--dim) !important;
}
div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }
div[data-testid="stRadio"] > div > label > div:last-child p {
  font-size: 11px !important; font-family: var(--mono) !important;
  color: var(--text2) !important; letter-spacing: 0.04em !important; line-height: 1 !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) > div:last-child p { color: var(--teal) !important; }

/* ── agent cards ── */
.panel-heading {
  font-size: 9px; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--text); margin-bottom: 10px; margin-top: 18px;
  display: flex; align-items: center; gap: 8px;
}
.panel-heading::after { content: ''; flex: 1; height: 1px; background: var(--border); }

.agent-card {
  border: 1px solid var(--border); border-radius: 6px;
  padding: 11px 13px; margin-bottom: 7px;
  background: var(--bg2); position: relative; overflow: hidden;
  transition: border-color 0.25s, background 0.25s;
}
.agent-card::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0;
  width: 2px; background: var(--ag-color); opacity: 0; transition: opacity 0.25s;
}
.agent-card.active { border-color: var(--ag-color); background: color-mix(in srgb, var(--ag-color) 5%, var(--bg2)); }
.agent-card.active::before { opacity: 1; }
.agent-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; }
.agent-name { display: flex; align-items: center; gap: 7px; font-size: 11px; font-weight: 500; color: var(--text2); }
.agent-card.active .agent-name { color: var(--ag-color); }
.agent-ico { font-size: 13px; }
.agent-badge {
  font-size: 8px; letter-spacing: 0.1em; padding: 2px 5px;
  border-radius: 3px; background: var(--border); color: var(--text); text-transform: uppercase;
}
.agent-card.active .agent-badge { background: color-mix(in srgb, var(--ag-color) 18%, var(--bg)); color: var(--ag-color); }
.agent-desc { font-size: 10px; color: var(--text); line-height: 1.5; margin-bottom: 5px; }
.agent-status { font-size: 9px; color: var(--text); }
.agent-card.active .agent-status { color: var(--ag-color); opacity: 0.8; }
.agent-bar { margin-top: 7px; height: 2px; background: var(--border); border-radius: 1px; display: none; overflow: hidden; }
.agent-card.active .agent-bar { display: block; }
.agent-fill { height: 100%; background: var(--ag-color); animation: sweep 1.8s ease-in-out infinite; }
@keyframes sweep { 0% { width: 0%; margin-left: 0; } 50% { width: 60%; margin-left: 20%; } 100% { width: 0%; margin-left: 100%; } }

/* ── query area ── */
.query-prefix { font-size: 11px; color: var(--teal); letter-spacing: 0.04em; margin-bottom: 6px; font-weight: 500; }
.stTextArea textarea {
  background: var(--bg2) !important; border: 1px solid var(--brd2) !important;
  border-radius: 6px !important; color: var(--text3) !important;
  font-family: var(--mono) !important; font-size: 13px !important;
  resize: none !important; line-height: 1.7 !important;
}
.stTextArea textarea:focus {
  border-color: var(--teal) !important;
  box-shadow: 0 0 0 1px rgba(0,255,179,0.12), 0 0 18px rgba(0,255,179,0.04) !important;
}
.stTextArea label { display: none !important; }

/* ── action buttons ── */
/* Run — col 1 */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
  background: var(--teal) !important; color: #080a0f !important; border: none !important;
  font-family: var(--mono) !important; font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: 0.08em !important; text-transform: uppercase !important;
  padding: 7px 12px !important; border-radius: 5px !important; transition: all 0.2s !important;
  white-space: nowrap !important; height: 36px !important; line-height: 1 !important;
  text-align: center !important; display: flex !important; align-items: center !important; justify-content: center !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
  background: #00e8a2 !important; box-shadow: 0 0 14px rgba(0,255,179,0.2) !important; transform: translateY(-1px) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:disabled {
  background: var(--border) !important; color: var(--text) !important; transform: none !important; box-shadow: none !important;
}
/* Clear — col 2 */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
  background: transparent !important; color: var(--text) !important;
  border: 1px solid var(--border) !important;
  font-family: var(--mono) !important; font-size: 10px !important;
  letter-spacing: 0.07em !important; text-transform: uppercase !important;
  padding: 7px 14px !important; border-radius: 5px !important;
  transition: all 0.2s !important;
  white-space: nowrap !important;
  height: 36px !important; line-height: 1 !important;
  text-align: center !important; display: flex !important; align-items: center !important; justify-content: center !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
  border-color: var(--red) !important; color: var(--red) !important;
}
/* Export — col 3 */
div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton > button {
  background: transparent !important; color: var(--text) !important;
  border: 1px solid var(--border) !important;
  font-family: var(--mono) !important; font-size: 10px !important;
  letter-spacing: 0.07em !important; text-transform: uppercase !important;
  padding: 7px 14px !important; border-radius: 5px !important;
  transition: all 0.2s !important;
  white-space: nowrap !important;
  height: 36px !important; line-height: 1 !important;
  text-align: center !important; display: flex !important; align-items: center !important; justify-content: center !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton > button:hover {
  border-color: var(--blue) !important; color: var(--blue) !important;
}
/* Download button */
.stDownloadButton > button {
  background: var(--bg2) !important; border: 1px solid var(--blue) !important; color: var(--blue) !important;
  font-family: var(--mono) !important; font-size: 10px !important; padding: 5px 12px !important; border-radius: 5px !important;
}
/* New session button */
.stButton.new-sess > button {
  background: transparent !important; border: 1px solid var(--border) !important;
  color: var(--text) !important; font-size: 10px !important; padding: 7px !important;
}

/* ── response panel ── */
.resp-panel { border: 1px solid var(--border); border-radius: 8px; background: var(--bg1); overflow: hidden; }
.resp-header {
  padding: 9px 16px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 9px;
}
.resp-lbl { font-size: 9px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text); }
.resp-spacer { flex: 1; }
.resp-tag { font-size: 9px; padding: 2px 7px; border-radius: 3px; background: var(--border); color: var(--text); letter-spacing: 0.06em; }
.resp-body {
  padding: 20px 22px; font-size: 13px; line-height: 1.8; color: var(--text2);
  min-height: 260px; max-height: 480px; overflow-y: auto;
}
.resp-body::-webkit-scrollbar { width: 4px; }
.resp-body::-webkit-scrollbar-thumb { background: var(--brd2); border-radius: 2px; }
.resp-body h2, .resp-body h3 { font-family: var(--disp); color: var(--text3); }
.resp-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; min-height: 240px; gap: 12px; color: var(--border);
}
.resp-empty-g { font-size: 20px; letter-spacing: 4px; }
.resp-empty-t { font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; }
.cur {
  display: inline-block; width: 6px; height: 13px; background: var(--teal);
  margin-left: 2px; vertical-align: middle;
  animation: blink 0.7s step-start infinite; border-radius: 1px;
}
@keyframes blink { 50% { opacity: 0; } }

/* orch banner */
.orch-banner {
  padding: 8px 16px; display: flex; align-items: center; gap: 10px;
  border-bottom: 1px solid color-mix(in srgb, var(--teal) 22%, transparent);
  background: color-mix(in srgb, var(--teal) 5%, var(--bg2));
}
.orch-lbl { font-size: 10px; color: var(--teal); letter-spacing: 0.05em; }
.orch-chips { display: flex; gap: 5px; margin-left: auto; }
.orch-chip {
  font-size: 9px; padding: 2px 7px; border-radius: 3px;
  border: 1px solid var(--teal); color: var(--teal); background: var(--bg);
  letter-spacing: 0.06em; animation: fadein 0.3s ease;
}
@keyframes fadein { from { opacity: 0; transform: translateY(2px); } to { opacity: 1; } }

/* attr bar */
.attr-bar { padding: 9px 16px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
.attr-lbl { font-size: 9px; color: var(--text); letter-spacing: 0.1em; text-transform: uppercase; }
.attr-chip { display: flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 20px; border: 1px solid var(--brd2); font-size: 9px; color: var(--text); background: var(--bg2); }
.attr-dot { width: 5px; height: 5px; border-radius: 50%; }
.attr-time { margin-left: auto; font-size: 9px; color: var(--text); }

/* ── log panel ── */
.log-hdr { display: flex; align-items: center; justify-content: space-between; font-size: 9px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text); margin-bottom: 10px; }
.log-cnt { padding: 2px 7px; border-radius: 10px; background: var(--border); font-size: 9px; color: var(--text); }
.log-empty { font-size: 10px; color: var(--brd2); letter-spacing: 0.06em; text-align: center; padding: 30px 0; }
.log-entry { border: 1px solid var(--border); border-radius: 5px; padding: 9px 11px; margin-bottom: 6px; background: var(--bg2); transition: border-color 0.2s; }
.log-entry:hover { border-color: var(--brd2); }
.log-entry.sel { border-color: var(--teal); }
.log-q { font-size: 10px; color: var(--text2); line-height: 1.5; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.log-meta { display: flex; align-items: center; gap: 5px; }
.log-ts { font-size: 9px; color: var(--text); }
.log-dur { font-size: 9px; color: var(--blue); margin-left: auto; }
.log-dots { display: flex; gap: 3px; align-items: center; }
.log-dot { width: 4px; height: 4px; border-radius: 50%; }

.session-box {
  border: 1px solid var(--border); border-radius: 5px; padding: 10px 12px;
  background: var(--bg2); margin-bottom: 8px;
  display: flex; align-items: center; justify-content: space-between;
}
.session-lbl { font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text); }
.session-id { font-size: 11px; color: var(--teal); font-weight: 500; }

.cache-box {
  border: 1px solid var(--border); border-radius: 5px; padding: 8px 12px;
  background: var(--bg2); margin-top: 10px;
  display: flex; align-items: center; justify-content: space-between;
}
.cache-lbl { font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text); }
.cache-val { font-size: 11px; color: var(--blue); font-weight: 500; }

.stStatus, [data-testid="stStatusWidget"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "session_id":      str(uuid.uuid4())[:8],
        "history":         [],
        "active_agents":   set(),
        "is_running":      False,
        "total_queries":   0,
        "current_mode":    "team",
        "query_cache":     {},
        "q_key":           0,    # incremented on Clear → resets textarea
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Helpers ───────────────────────────────────────────────────────────────────
def query_hash(q: str, mode: str) -> str:
    return hashlib.md5(f"{q.strip().lower()}:{mode}".encode()).hexdigest()[:10]


@st.cache_data(ttl=5)
def check_server() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def call_team(query: str, session_id: str):
    url  = f"{API_BASE}/teams/{TEAM_ID}/runs"
    data = {"message": query, "stream": "true", "session_id": session_id}
    try:
        with requests.post(url, data=data, stream=True, timeout=180) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    yield chunk
    except requests.exceptions.ConnectionError:
        yield "⚠  Cannot reach server at localhost:7777. Is `python app.py` running?"
    except requests.exceptions.Timeout:
        yield "⚠  Request timed out (>3 min). Try a more focused query."
    except Exception as e:
        yield f"⚠  Error: {e}"



def md_to_html(text: str) -> str:
    """Lightweight markdown to HTML converter for unsafe_allow_html rendering."""
    import re as _re
    text = _re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=_re.MULTILINE)
    text = _re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=_re.MULTILINE)
    text = _re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=_re.MULTILINE)
    text = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = _re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    lines, out, in_ul = text.split('\n'), [], False
    for line in lines:
        if _re.match(r'^- (.+)', line):
            if not in_ul: out.append('<ul>'); in_ul = True
            out.append('<li>' + line[2:] + '</li>')
        else:
            if in_ul: out.append('</ul>'); in_ul = False
            out.append(line)
    if in_ul: out.append('</ul>')
    text = '\n'.join(out)
    text = _re.sub(r'(<h[123]>.*?</h[123]>)', r'\1', text)
    text = _re.sub(r'(?<!>)\n\n+(?!<)', '<br><br>', text)
    text = _re.sub(r'(?<!>)\n(?!<)', '<br>', text)
    return text

def extract_content(raw: str) -> str:
    """Pull the content field from a JSON response, fallback to raw text."""
    try:
        payload = json.loads(raw)
        return payload.get("content", raw)
    except Exception:
        return raw


def call_agent(agent_id: str, query: str) -> str:
    url, data, delay = f"{API_BASE}/agents/{agent_id}/runs", {"message": query, "stream": "false"}, 1.5
    for attempt in range(3):
        try:
            r = requests.post(url, data=data, timeout=120)
            r.raise_for_status()
            return extract_content(r.text)
        except requests.exceptions.ConnectionError:
            return "⚠  Cannot reach server at localhost:7777."
        except requests.exceptions.HTTPError as e:
            if attempt < 2:
                time.sleep(delay); delay *= 2; continue
            return f"⚠  HTTP Error: {e}"
        except Exception as e:
            return f"⚠  Error: {e}"
    return "⚠  Max retries exceeded."


def detect_agents(text: str) -> set:
    found, lower = set(), text.lower()
    for a_id in AGENT_IDS:
        if AGENT_META[a_id]["label"].lower() in lower or a_id in lower:
            found.add(a_id)
    return found


# ── Render ────────────────────────────────────────────────────────────────────
server_ok    = check_server()
history      = st.session_state.history
last_item    = history[-1] if history else None
mode         = st.session_state.current_mode
mode_display = "Team" if mode == "team" else AGENT_META.get(mode, {}).get("short", "—")

# ── TOP BAR ───────────────────────────────────────────────────────────────────
srv_cls = "live" if server_ok else ""
srv_txt = "LIVE · :7777" if server_ok else "OFFLINE"
st.markdown(f"""
<div class="vr-topbar">
  <div class="vr-logo">
    <div class="vr-logo-mark">◈</div>
    VALYU RESEARCH OS
  </div>
  <div class="spacer"></div>
  <div class="vr-stat">
    <div class="vr-stat-v">{st.session_state.total_queries}</div>
    <div class="vr-stat-l">Queries</div>
  </div>
  <div class="vr-sep"></div>
  <div class="vr-stat">
    <div class="vr-stat-v">{mode_display}</div>
    <div class="vr-stat-l">Mode</div>
  </div>
  <div class="vr-sep"></div>
  <div class="vr-stat">
    <div class="vr-stat-v">{str(last_item['duration']) + 's' if last_item else '—'}</div>
    <div class="vr-stat-l">Last Run</div>
  </div>
  <div class="vr-sep"></div>
  <div class="vr-stat" style="flex-direction:row;align-items:center;gap:0">
    <span class="srv-dot {srv_cls}"></span>
    <div>
      <div class="vr-stat-v" style="font-size:11px">{srv_txt}</div>
      <div class="vr-stat-l">Server</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── THREE COLUMNS ─────────────────────────────────────────────────────────────
left_col, center_col, right_col = st.columns([0.22, 0.52, 0.26], gap="large")


# ── LEFT: Route + Agents ──────────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="panel-heading" style="margin-top:4px">Route</div>', unsafe_allow_html=True)

    # Real st.radio — handles state, reruns on change, styled as button list via CSS
    current_label = LABEL_BY_MODE.get(st.session_state.current_mode, MODE_LABELS[0])
    selected = st.radio(
        "Route",
        MODE_LABELS,
        index=MODE_LABELS.index(current_label),
        key="mode_radio",
        label_visibility="collapsed",
    )
    new_mode = MODE_BY_LABEL[selected]
    if new_mode != st.session_state.current_mode:
        st.session_state.current_mode = new_mode
        st.rerun()

    st.markdown('<div class="panel-heading">Agents</div>', unsafe_allow_html=True)
    active_set = st.session_state.active_agents
    for a_id in AGENT_IDS:
        m      = AGENT_META[a_id]
        is_act = a_id in active_set
        cls    = "agent-card active" if is_act else "agent-card"
        task   = m["tasks"][int(time.time()) % len(m["tasks"])] if is_act else "· idle"
        st.markdown(f"""
        <div class="{cls}" style="--ag-color:{m['color']}">
          <div class="agent-top">
            <div class="agent-name"><span class="agent-ico">{m['icon']}</span>{m['label']}</div>
            <div class="agent-badge">{m['short']}</div>
          </div>
          <div class="agent-desc">{m['description']}</div>
          <div class="agent-status">{"▸ " + task if is_act else task}</div>
          <div class="agent-bar"><div class="agent-fill"></div></div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.query_cache:
        st.markdown(f"""
        <div class="cache-box">
          <span class="cache-lbl">Cache</span>
          <span class="cache-val">{len(st.session_state.query_cache)} stored</span>
        </div>
        """, unsafe_allow_html=True)


# ── CENTER: Query + Response ──────────────────────────────────────────────────
with center_col:
    st.markdown('<div class="query-prefix">~/research $</div>', unsafe_allow_html=True)

    # q_key increments on Clear, giving the textarea a new key and resetting its value
    query = st.text_area(
        "Query",
        placeholder="What are the latest advances in GLP-1 receptor agonists for obesity?\n\nThe team will coordinate automatically.",
        height=90,
        label_visibility="collapsed",
        disabled=st.session_state.is_running,
        key=f"qi_{st.session_state.q_key}",
    )

    # Compact button row — fixed column sizes
    c_run, c_clear, c_export, _ = st.columns([1, 1, 1, 3])
    with c_run:
        run_clicked = st.button(
            "▶  Run" if not st.session_state.is_running else "⏳  Running…",
            disabled=st.session_state.is_running or not (query or "").strip() or not server_ok,
            use_container_width=True,
            key="btn_run",
        )
    with c_clear:
        clear_clicked = st.button("✕ Clear", disabled=st.session_state.is_running,
                                  use_container_width=True, key="btn_clear")
    with c_export:
        export_clicked = st.button("⬇ Export", disabled=not history,
                                   use_container_width=True, key="btn_export")

    # Clear: increment key → textarea reinitialises empty
    if clear_clicked:
        st.session_state.q_key += 1
        st.rerun()

    # Export: show download button below action row
    if export_clicked and history:
        li = history[-1]
        md = (f"# Valyu Research Export\n\n"
              f"**Query:** {li['query']}\n\n"
              f"**Time:** {li['ts']}  |  **Duration:** {li['duration']}s  |  "
              f"**Agents:** {', '.join(li.get('agents_used', []))}\n\n---\n\n{li['response']}")
        st.download_button("Download .md", data=md,
                           file_name=f"valyu_{li['ts'].replace(':', '')}.md",
                           mime="text/markdown", key="dl_btn")

    # Response panel header
    mode_lbl   = "TEAM ORCHESTRATION" if mode == "team" else AGENT_META.get(mode, {}).get("label", "").upper()
    status_tag = "STREAMING" if st.session_state.is_running else "READY"
    st.markdown(f"""
    <div class="resp-panel">
      <div class="resp-header">
        <span class="resp-lbl">Research Output</span>
        <span class="resp-tag">{mode_lbl}</span>
        <div class="resp-spacer"></div>
        <span class="resp-tag">{status_tag}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    orch_ph = st.empty()
    resp_ph = st.empty()
    attr_ph = st.empty()

    if not st.session_state.is_running:
        if history:
            li = history[-1]
            resp_ph.markdown(f'<div class="resp-body">{md_to_html(li["response"])}</div>', unsafe_allow_html=True)
            chips = "".join(
                f'<div class="attr-chip"><div class="attr-dot" style="background:{AGENT_META[a]["color"]}"></div>'
                f'{AGENT_META[a]["label"]}</div>'
                for a in li.get("agents_used", []) if a in AGENT_META
            )
            if chips:
                attr_ph.markdown(
                    f'<div class="attr-bar"><span class="attr-lbl">via</span>{chips}'
                    f'<span class="attr-time">{li["duration"]}s</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            resp_ph.markdown(
                '<div class="resp-body"><div class="resp-empty">'
                '<div class="resp-empty-g">◈ ◎ ◐ ◉</div>'
                '<div class="resp-empty-t">Awaiting research query</div>'
                '</div></div>',
                unsafe_allow_html=True,
            )


# ── RIGHT: Log + Session ──────────────────────────────────────────────────────
with right_col:
    st.markdown(f"""
    <div class="log-hdr">
      Query Log <span class="log-cnt">{len(history)}</span>
    </div>
    """, unsafe_allow_html=True)

    if not history:
        st.markdown('<div class="log-empty">No queries yet</div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(history)):
            sel   = "sel" if i == 0 else ""
            short = item["query"][:75] + "…" if len(item["query"]) > 75 else item["query"]
            dots  = "".join(
                f'<div class="log-dot" style="background:{AGENT_META[a]["color"]}"></div>'
                for a in item.get("agents_used", []) if a in AGENT_META
            )
            st.markdown(f"""
            <div class="log-entry {sel}">
              <div class="log-q">{short}</div>
              <div class="log-meta">
                <div class="log-dots">{dots}</div>
                <span class="log-ts">{item["ts"]}</span>
                <span class="log-dur">{item["duration"]}s</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="session-box" style="margin-top:14px">
      <span class="session-lbl">Session</span>
      <span class="session-id">{st.session_state.session_id}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⟳  New Session", use_container_width=True, key="new_session"):
        for k in ("session_id", "history", "total_queries", "query_cache"):
            st.session_state[k] = str(uuid.uuid4())[:8] if k == "session_id" else ([] if k == "history" else (0 if k == "total_queries" else {}))
        st.session_state.q_key += 1
        st.rerun()


# ── Run Logic ─────────────────────────────────────────────────────────────────
if run_clicked and (query or "").strip():
    q      = query.strip()
    q_hash = query_hash(q, st.session_state.current_mode)

    # Cache hit
    if q_hash in st.session_state.query_cache:
        cached = st.session_state.query_cache[q_hash]
        with center_col:
            orch_ph.markdown(
                '<div class="orch-banner"><span class="orch-lbl">◈ Cache hit — returning stored result</span></div>',
                unsafe_allow_html=True,
            )
            resp_ph.markdown(f'<div class="resp-body">{md_to_html(cached["response"])}</div>', unsafe_allow_html=True)
        st.session_state.history.append({**cached, "query": q, "ts": time.strftime("%H:%M")})
        st.session_state.total_queries += 1
        time.sleep(0.5)
        st.rerun()

    # Live run
    st.session_state.is_running    = True
    st.session_state.active_agents = set()
    start_t       = time.time()
    full_response = ""
    agents_seen: set = set()
    run_mode = st.session_state.current_mode

    with center_col:
        if run_mode == "team":
            orch_ph.markdown(
                '<div class="orch-banner"><span class="orch-lbl">◈ Orchestrator routing query…</span></div>',
                unsafe_allow_html=True,
            )
            for chunk in call_team(q, st.session_state.session_id):
                full_response += chunk
                new_a = detect_agents(full_response)
                if new_a != agents_seen:
                    agents_seen = new_a
                    st.session_state.active_agents = agents_seen
                    chips = "".join(
                        f'<div class="orch-chip">{AGENT_META[a]["short"]}</div>'
                        for a in agents_seen if a in AGENT_META
                    )
                    orch_ph.markdown(
                        f'<div class="orch-banner">'
                        f'<span class="orch-lbl">◈ Coordinating {len(agents_seen)} agent(s)</span>'
                        f'<div class="orch-chips">{chips}</div></div>',
                        unsafe_allow_html=True,
                    )
                resp_ph.markdown(
                    f'<div class="resp-body">{md_to_html(full_response)}<span class="cur"></span></div>',
                    unsafe_allow_html=True,
                )
            orch_ph.markdown(
                '<div class="orch-banner" style="background:color-mix(in srgb,var(--blue) 5%,var(--bg2));'
                'border-color:color-mix(in srgb,var(--blue) 25%,transparent)">'
                '<span class="orch-lbl" style="color:var(--blue)">✓ Synthesis complete</span></div>',
                unsafe_allow_html=True,
            )

        else:
            agents_seen = {run_mode}
            st.session_state.active_agents = agents_seen
            ac = AGENT_META[run_mode]["color"]
            orch_ph.markdown(
                f'<div class="orch-banner" style="background:color-mix(in srgb,{ac} 5%,var(--bg2));'
                f'border-color:color-mix(in srgb,{ac} 25%,transparent)">'
                f'<span class="orch-lbl" style="color:{ac}">{AGENT_META[run_mode]["icon"]} Running {AGENT_META[run_mode]["label"]}…</span></div>',
                unsafe_allow_html=True,
            )
            resp_ph.markdown('<div class="resp-body"><span class="cur"></span></div>', unsafe_allow_html=True)
            full_response = call_agent(run_mode, q)
            orch_ph.markdown(
                f'<div class="orch-banner" style="background:color-mix(in srgb,{ac} 5%,var(--bg2));'
                f'border-color:color-mix(in srgb,{ac} 25%,transparent)">'
                f'<span class="orch-lbl" style="color:{ac}">✓ {AGENT_META[run_mode]["label"]} complete</span></div>',
                unsafe_allow_html=True,
            )

        full_response = extract_content(full_response)
        resp_ph.markdown(f'<div class="resp-body">{md_to_html(full_response)}</div>', unsafe_allow_html=True)
        chips = "".join(
            f'<div class="attr-chip"><div class="attr-dot" style="background:{AGENT_META[a]["color"]}"></div>'
            f'{AGENT_META[a]["label"]}</div>'
            for a in agents_seen if a in AGENT_META
        )
        duration = round(time.time() - start_t, 1)
        if chips:
            attr_ph.markdown(
                f'<div class="attr-bar"><span class="attr-lbl">via</span>{chips}'
                f'<span class="attr-time">{duration}s</span></div>',
                unsafe_allow_html=True,
            )

    entry = {
        "query": q, "response": full_response, "ts": time.strftime("%H:%M"),
        "agents_used": list(agents_seen), "duration": duration,
    }
    st.session_state.history.append(entry)
    st.session_state.query_cache[q_hash] = entry
    st.session_state.total_queries      += 1
    st.session_state.is_running          = False
    st.session_state.active_agents       = set()
    st.rerun()