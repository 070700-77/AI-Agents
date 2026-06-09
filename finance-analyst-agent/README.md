# Warren — AI Financial Analyst Agent 📈

Warren is a conversational AI agent specialized in real-time financial analysis. He can search for stocks, retrieve live quotes, analyze company fundamentals, review historical price data, screen the market, and fetch the latest financial news — all through natural language.

---

## What Problem It Solves

Financial analysis typically requires switching between multiple tools, APIs, and dashboards. Warren centralizes all of that into a single conversational interface backed by live Yahoo Finance data and LLM-powered interpretation.

---

## How It Works

1. Warren loads his personality from `system_prompt.txt` at startup.
2. Conversation history is persisted in `memory.db` (SQLite).
3. The **inner agentic loop** maps natural language requests to specific Yahoo Finance API endpoints:
   - ` ```action ` blocks trigger the appropriate `connect_api` function.
   - Results are parsed, filtered, and injected back as structured context.
   - The LLM synthesizes the data into actionable financial insight.

**Two versions are available:**

| Version | Description                              | File         |
|---------|------------------------------------------|--------------|
| CLI     | Terminal-based conversational agent      | `agent.py`   |
| Web UI  | FastAPI + streaming frontend in browser  | `web/app.py` |

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**Finance API:** [Yahoo Finance 15](https://rapidapi.com/sparior/api/yahoo-finance15) via RapidAPI

---

## Available Tools

| Tool                 | Endpoint                              | Description                          |
|----------------------|---------------------------------------|--------------------------------------|
| `v1_search`          | `/api/v1/markets/search`              | Search for any stock or asset        |
| `v1_market_quotes`   | `/api/v1/markets/quote`               | Live price, P/E, market cap, etc.    |
| `v1_stock_modules`   | `/api/v1/markets/stock/modules`       | Company profile & financial data     |
| `v2_stock_history`   | `/api/v2/markets/stock/history`       | Historical OHLCV price data          |
| `v1_market_screener` | `/api/v1/markets/screener`            | Market screener by category          |
| `v2_market_news`     | `/api/v2/markets/news`                | Latest news for a given ticker       |

---

## External APIs

| Service              | Purpose                          | Key Required |
|----------------------|----------------------------------|-------------|
| Anthropic            | LLM inference via LiteLLM        | Yes         |
| RapidAPI (YFinance)  | Live financial data              | Yes         |

---

## Environment Variables

| Variable            | Description                                             |
|---------------------|---------------------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com       |
| `X_RAPIDAPI_KEY`    | Your RapidAPI key from rapidapi.com                     |

---

## Setup — CLI Version

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Agents.git
cd AI-Agents/finance-analyst-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install litellm python-dotenv

# 4. Configure environment variables
cp .env.example .env
# Open .env and add your real credentials

# 5. Run the agent
python agent.py
```

---

## Setup — Web UI Version

```bash
cd AI-Agents/finance-analyst-agent/web

# Install additional dependencies
pip install fastapi uvicorn python-dotenv litellm

# Copy the .env.example from the parent folder
cp ../.env.example .env
# Open .env and add your real credentials

# Run the server
python app.py
# Then open http://localhost:8000 in your browser
```

---

## How to Run

**CLI:**
```bash
python agent.py
```

**Web UI:**
```bash
cd web && python app.py
```

Example prompts:
- `Search for Apple stock`
- `What's the current price of TSLA?`
- `Show me NVDA's financial fundamentals`
- `Get AAPL historical data for the last year`
- `Screen the most active stocks today`

---

## ⚠️ Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values — it is safe to commit.

---

## Agent Persona

**Name:** Warren  
**Role:** AI financial analyst  
**Memory:** Persistent (SQLite — last 20 messages per session)  
**Termination:** Automatic via `terminate` block in LLM response
