# Finance Teacher Agent

A private finance tutor that teaches financial mathematics, asset valuation, project evaluation and financial statement analysis step by step — using real company data instead of abstract textbook examples.

---

## What Problem It Solves

Learning finance from static material makes it hard to connect theory with real companies. This agent adapts to the student's level (with short diagnostic tests), explains concepts progressively, and pulls real income statements, balance sheets and cash flows so every lesson is grounded in actual data. It is instructed never to invent financial figures.

---

## How It Works

1. The agent loads its personality, rules and tool definitions from `system_prompt.txt`.
2. Conversation history is persisted in a local `memory.db` (SQLite). The last 20 messages are recalled on every start, so the agent remembers earlier sessions.
3. On each user message, the **agentic loop** runs:
   - The LLM decides whether it needs external data.
   - If it does, it answers with an ` ```action ` block containing a `tool_name` and its `args`.
   - The program parses the block, a router calls the matching financial data endpoint, and the result is fed back to the LLM.
   - The loop repeats until the LLM answers in plain text, which is printed to the user.
4. When the user says goodbye, the LLM emits a `terminate` block and the program exits gracefully.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**External API:** [Real-Time Finance Data](https://rapidapi.com/) via RapidAPI (`real-time-finance-data.p.rapidapi.com`)

---

## Available Tools

| Tool                       | Description |
|----------------------------|-------------|
| `company_overview`         | Price, market cap, P/E, sector, exchange and general stock info |
| `company_income_statement` | Annual or quarterly income statement |
| `company_balance_sheet`    | Annual or quarterly balance sheet |
| `company_cash_flow`        | Annual or quarterly cash-flow statement |

---

## External APIs

| Service   | Purpose                  | Key Required |
|-----------|--------------------------|--------------|
| Anthropic | LLM inference via LiteLLM | Yes          |
| Real-Time Finance Data | Company overview and financial statements | Yes (RapidAPI key) |

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
cd AI-Agents/finance-teacher-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env          # Windows: copy .env.example .env
# Open .env and add your ANTHROPIC_API_KEY and X_RAPIDAPI_KEY

# 5. Subscribe to the API on RapidAPI (real-time-finance-data) with your key
```

---

## How to Run

```bash
python agent.py
```

Example prompts:

- `Teach me the difference between nominal and effective interest rates.`
- `Show me Apple's latest annual income statement and explain the key lines.`
- `Quiz me on NPV and IRR.`

---

## Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values and is safe to commit. The local `memory.db` (your conversation history) is also git-ignored.

---

## Agent Persona

**Role:** Private finance professor focused on institutional-style investing and case-based learning  
**Language:** Spanish  
**Memory:** Persistent (SQLite — last 20 messages)  
**Note:** The bundled `system_prompt.txt` is personalized for the author's learning profile. Edit the *identity/student* section to match your own background before using it.  
**Termination:** Automatic via `terminate` block in the LLM response
