# Topo — Earthquake Analyzer Agent

Topo is a seismology assistant that queries recent earthquakes anywhere in the world and explains the data in simple, accurate language.

---

## What Problem It Solves

Raw earthquake feeds are hard to filter and interpret. Topo translates natural-language requests ("the strongest quakes in Chile this week") into structured API queries — converting places into coordinates and radii — and then explains magnitudes, locations and context without speculating.

---

## How It Works

1. The agent loads its personality, rules and tool definitions from `system_prompt.txt`.
2. Conversation history is persisted in a local `memory.db` (SQLite). The last 20 messages are recalled on every start, so the agent remembers earlier sessions.
3. On each user message, the **agentic loop** runs:
   - The LLM decides whether it needs external data.
   - If it does, it answers with an ` ```action ` block containing a `tool_name` and its `args`.
   - The program parses the block, a router calls the matching EveryEarthquake endpoint, and the result is fed back to the LLM.
   - The loop repeats until the LLM answers in plain text, which is printed to the user.
4. When the user says goodbye, the LLM emits a `terminate` block and the program exits gracefully.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**External API:** [EveryEarthquake](https://rapidapi.com/dbarkman/api/everyearthquake) via RapidAPI (`everyearthquake.p.rapidapi.com`)

---

## Available Tools

| Tool                 | Description |
|----------------------|-------------|
| `recent_earthquakes` | Recent earthquakes filtered by interval (hour/day/week/month), start date, count, type, latitude/longitude/radius, units (km/miles), minimum magnitude and intensity |

---

## External APIs

| Service   | Purpose                  | Key Required |
|-----------|--------------------------|--------------|
| Anthropic | LLM inference via LiteLLM | Yes          |
| EveryEarthquake | Real-time and recent earthquake data | Yes (RapidAPI key) |

---

## Environment Variables

| Variable            | Description                                       |
|---------------------|---------------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com |
| `X_RAPIDAPI_KEY`    | Your RapidAPI key from rapidapi.com               |

Both are read with `os.getenv()` after `load_dotenv()`. Copy `.env.example` to `.env` and fill in your own values.

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/070700-77/AI-Agents.git
cd AI-Agents/earthquake-analyzer-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env          # Windows: copy .env.example .env
# Open .env and add your ANTHROPIC_API_KEY and X_RAPIDAPI_KEY

# 5. Subscribe to the API on RapidAPI (everyearthquake) with your key
```

---

## How to Run

```bash
python agent.py
```

Example prompts:

- `What earthquakes happened in the last 24 hours?`
- `Show me magnitude 5+ quakes near Colombia this week.`
- `Were there any strong earthquakes in Japan this month?`

---

## Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values and is safe to commit. The local `memory.db` (your conversation history) is also git-ignored.

---

## Agent Persona

**Name:** Topo  
**Role:** Curious, clear and direct seismology assistant  
**Language:** Spanish  
**Memory:** Persistent (SQLite — last 20 messages)  
**Termination:** Automatic via `terminate` block in the LLM response
