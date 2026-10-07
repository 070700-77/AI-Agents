# Finance Analyst (Full) Agent

An investment-committee-style AI analyst for public markets. It combines fundamental thinking, technical indicators, options data and market news through the full Yahoo Finance API, with a strict rule against fabricating data. Its persona is inspired by Charlie Munger's investment philosophy (it does not claim to be the real person).

---

## What Problem It Solves

Retail and student investors rarely get a structured, skeptical second opinion. This agent screens opportunities, pulls live quotes, history, calendars, options activity and indicators, separates facts from inferences and assumptions, and explicitly weighs risk of permanent capital loss — instead of just agreeing with the user. This is the extended version of the simpler [`finance-analyst-agent`](../finance-analyst-agent/).

---

## How It Works

1. The agent loads its personality, rules and tool definitions from `system_prompt.txt`.
2. Conversation history is persisted in a local `memory.db` (SQLite). The last 20 messages are recalled on every start, so the agent remembers earlier sessions.
3. On each user message, the **agentic loop** runs:
   - The LLM decides whether it needs external data.
   - If it does, it answers with an ` ```action ` block containing a `tool_name` and its `args`.
   - The program parses the block, a router calls the matching Yahoo Finance endpoint, and the result is fed back to the LLM.
   - The loop repeats until the LLM answers in plain text, which is printed to the user.
4. When the user says goodbye, the LLM emits a `terminate` block and the program exits gracefully.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**External API:** [Yahoo Finance](https://rapidapi.com/) via RapidAPI (`yahoo-finance15.p.rapidapi.com`)

---

## Available Tools

A single `search`/router layer exposes the following Yahoo Finance endpoints:

| Group | Endpoints |
|-------|-----------|
| Market data | `market_tickers`, `search`, `market_quotes_realtime`, `market_quotes_snapshots`, `market_screener` |
| News & insiders | `market_news_v1`, `market_news_v2`, `insider_trades` |
| History | `stock_history_v1`, `stock_history_v2` |
| Calendars | `calendar_earnings`, `calendar_dividends`, `calendar_economic_events`, `calendar_public_offerings`, `calendar_ipo`, `calendar_stock_splits` |
| Options | `options`, `unusual_options_activity`, `most_active` |
| Technical indicators | `indicator_sma`, `indicator_rsi`, `indicator_adx`, `indicator_macd` |

---

## External APIs

| Service   | Purpose                  | Key Required |
|-----------|--------------------------|--------------|
| Anthropic | LLM inference via LiteLLM | Yes          |
| Yahoo Finance | Quotes, history, news, calendars, options and indicators | Yes (RapidAPI key) |

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
cd AI-Agents/finance-analyst-full-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env          # Windows: copy .env.example .env
# Open .env and add your ANTHROPIC_API_KEY and X_RAPIDAPI_KEY

# 5. Subscribe to the API on RapidAPI (yahoo-finance15) with your key
```

---

## How to Run

```bash
python agent.py
```

Example prompts:

- `Search for Nvidia and show me its latest quote.`
- `What are the upcoming earnings this week?`
- `Show me RSI and MACD for AAPL and tell me what they suggest.`

---

## Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values and is safe to commit. The local `memory.db` (your conversation history) is also git-ignored.

---

## Agent Persona

**Name:** Charlie Munger (investment-philosophy persona, not the historical person)  
**Role:** Senior investment manager / investment committee advisor  
**Language:** English  
**Memory:** Persistent (SQLite — last 20 messages)  
**Termination:** Automatic via `terminate` block in the LLM response
