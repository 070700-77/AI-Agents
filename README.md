# AI Agents 🤖

A collection of conversational AI agents built with Python, LiteLLM, and the Anthropic Claude API. Each agent has persistent memory, a defined persona, and real-world tool integrations.

---

## Agents

| Agent | Persona | Tools | APIs Used |
|-------|---------|-------|-----------|
| [Entrepreneurship Coach](./entrepreneurship-coach-agent/) | Roy — Strategy & startup coach | Memory only | Anthropic |
| [File Manager](./file-manager-agent/) | Koda — File system assistant | list_files, read_file, word_count | Anthropic |
| [News Updater](./news-updater-agent/) | Juli — Real-time news analyst | Real-Time News API | Anthropic + RapidAPI |
| [Job Seeker](./jobseeker-agent/) | Joshua — Job search assistant | LinkedIn Jobs API | Anthropic + RapidAPI |
| [Finance Analyst](./finance-analyst-agent/) | Warren — Financial analyst (CLI + Web) | Yahoo Finance API | Anthropic + RapidAPI |
| [Flight Finder](./flight-finder-agent/) | Valya — Travel & booking assistant | Google Flights API | Anthropic + RapidAPI |
| [Cacao Expert](./cocoa-expert-agent/) | Jose — Colombian cacao data expert | datos.gov.co API | Anthropic |

---

## Architecture Pattern

All agents share a common architecture:

```
User Input
    ↓
LLM (Claude via LiteLLM)
    ↓
Does response contain ```action block?
    ├── YES → Execute tool → Feed result back to LLM → Loop
    └── NO  → Print response to user → Wait for next input
                        ↓
              Does response contain ```terminate?
                    └── YES → Exit gracefully
```

Each agent also:
- Loads a `system_prompt.txt` to define its persona and rules
- Persists conversation history in a local `memory.db` (SQLite)
- Uses `python-dotenv` to load credentials from a `.env` file

---

## Security

- All API credentials are loaded from environment variables via `.env`
- **No credentials are hardcoded anywhere in the codebase**
- Each agent folder has a `.env.example` with placeholder values only
- `.gitignore` prevents `.env` files and `*.db` memory files from being committed

---

## Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)
- A [RapidAPI key](https://rapidapi.com/) (for agents that use external APIs)

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Agents.git
cd AI-Agents

# 2. Choose an agent, e.g.:
cd entrepreneurship-coach-agent

# 3. Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install litellm python-dotenv

# 4. Set up credentials
cp .env.example .env
# Edit .env with your real API keys

# 5. Run
python agent.py
```

---

## Project Structure

```
AI-Agents/
├── README.md
├── entrepreneurship-coach-agent/
│   ├── agent.py
│   ├── system_prompt.txt
│   ├── README.md
│   ├── .env.example
│   └── .gitignore
├── file-manager-agent/
├── news-updater-agent/
├── jobseeker-agent/
├── finance-analyst-agent/
│   ├── agent.py           ← CLI version
│   ├── web/
│   │   ├── app.py         ← FastAPI + streaming web UI
│   │   ├── requirements.txt
│   │   └── static/
│   ├── system_prompt.txt
│   ├── README.md
│   ├── .env.example
│   └── .gitignore
├── flight-finder-agent/
└── cocoa-expert-agent/
```

---

## ⚠️ Security Warning

**Never commit your `.env` files to GitHub.** They contain real API keys that could be exploited if exposed. Every folder has a `.gitignore` that excludes `.env` by default.
