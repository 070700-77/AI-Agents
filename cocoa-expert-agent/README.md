# Jose — Colombian Cacao Expert Agent 🍫

Jose is a conversational AI agent specialized in Colombian cacao production data. He queries the official Colombian government open data API to provide real-time statistics on production by department, top producing municipalities, and yield trends.

---

## What Problem It Solves

Colombia is one of the world's top fine cacao producers, but its production data is scattered across government portals. Jose makes that data conversational — you ask a question in plain Spanish or English and he retrieves, aggregates, and interprets the real numbers.

---

## How It Works

1. Jose loads his personality from `system_prompt.txt` at startup.
2. Conversation history is persisted in `memory.db` (SQLite).
3. When you ask about cacao data, the **inner agentic loop** runs:
   - ` ```action ` blocks trigger one of three API functions.
   - The government API ([datos.gov.co](https://www.datos.gov.co)) is queried with the appropriate filters.
   - Results are returned as JSON and injected back into the LLM context.
   - Jose interprets the data and answers your question.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**Data API:** [datos.gov.co](https://www.datos.gov.co/resource/24jd-fsbf.json) — Colombian Government Open Data (no API key required)

---

## Available Tools

| Tool                         | Description                                                        |
|------------------------------|--------------------------------------------------------------------|
| `produccion_x_departamento`  | Production data filtered by Colombian department                   |
| `top_municipios_produccion`  | Top N municipalities ranked by total production (tons)             |
| `rendimiento_x_departamento` | Yield (tons/hectare) by department, sorted by most recent year     |

---

## External APIs

| Service              | Purpose                               | Key Required |
|----------------------|---------------------------------------|-------------|
| Anthropic            | LLM inference via LiteLLM             | Yes         |
| datos.gov.co         | Colombian cacao production open data  | **No**      |

---

## Environment Variables

| Variable            | Description                                             |
|---------------------|---------------------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com       |

No API key is needed for the government data service.

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Agents.git
cd AI-Agents/cocoa-expert-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install litellm python-dotenv

# 4. Configure your environment variables
cp .env.example .env
# Open .env and add your real ANTHROPIC_API_KEY

# 5. Run the agent
python agent.py
```

---

## How to Run

```bash
python agent.py
```

Example prompts:
- `¿Cuáles son los municipios con mayor producción de cacao en Colombia?`
- `Dame los datos de producción del departamento de Santander`
- `¿Cuál es el rendimiento por hectárea en Huila?`
- `Top 10 producing municipalities`

---

## ⚠️ Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values — it is safe to commit.

---

## Agent Persona

**Name:** Jose  
**Role:** AI Colombian Cacao Expert  
**Memory:** Persistent (SQLite — last 20 messages per session)  
**Data Source:** Official Colombian government open data  
**Termination:** Automatic via `terminate` block in LLM response
