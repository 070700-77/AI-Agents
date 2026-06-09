# Juli — Real-Time News Updater Agent 📰

Juli is a conversational AI agent that fetches and summarizes live news headlines on any topic you request. She never invents stories — every headline comes directly from the RapidAPI News API.

---

## What Problem It Solves

LLMs have a training cutoff and cannot report on current events. Juli bridges that gap by combining an LLM's understanding of your request with a real-time news API call, then synthesizing the results into a clear, structured summary.

---

## How It Works

1. Juli loads her personality from `system_prompt.txt` at startup.
2. Conversation history is persisted in `memory.db` (SQLite).
3. When you ask for news, the **inner agentic loop** runs:
   - The LLM maps your request to an API call (topic, country, language, limit).
   - An ` ```action ` block triggers the `access_news_api` function.
   - The API result (titles, links, dates, sources) is injected back into the conversation.
   - The LLM synthesizes and presents the headlines.
4. Juli clearly distinguishes between live API data and her own analysis.

**LLM used:** `anthropic/claude-sonnet-4-5` via LiteLLM  
**News API:** [Real-Time News Data](https://rapidapi.com/letscrape-6bRB4T0ibU/api/real-time-news-data) via RapidAPI

---

## Available Tools

| Tool               | Description                                               |
|--------------------|-----------------------------------------------------------|
| `access_news_api`  | Fetches real-time headlines by topic, country, language   |

---

## External APIs

| Service             | Purpose                          | Key Required |
|---------------------|----------------------------------|-------------|
| Anthropic           | LLM inference via LiteLLM        | Yes         |
| RapidAPI (News)     | Real-time news headlines         | Yes         |

---

## Environment Variables

| Variable            | Description                                             |
|---------------------|---------------------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com       |
| `X_RAPIDAPI_KEY`    | Your RapidAPI key from rapidapi.com                     |

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Agents.git
cd AI-Agents/news-updater-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install litellm python-dotenv

# 4. Configure your environment variables
cp .env.example .env
# Open .env and add your ANTHROPIC_API_KEY and X_RAPIDAPI_KEY

# 5. Run the agent
python agent.py
```

---

## How to Run

```bash
python agent.py
```

Example prompts:
- `Give me the latest tech news`
- `What's happening in finance today?`
- `Top 3 sports headlines from Spain in Spanish`

---

## ⚠️ Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values — it is safe to commit.

---

## Agent Persona

**Name:** Juli  
**Role:** Real-time news analyst  
**Memory:** Persistent (SQLite — last 20 messages per session)  
**Termination:** Automatic via `terminate` block in LLM response
