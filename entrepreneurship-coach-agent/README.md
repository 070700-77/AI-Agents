# Roy — Entrepreneurship Coach Agent 🚀

Roy is a conversational AI agent that acts as your personal entrepreneurship, strategy, and business growth coach. He helps you think like a high-level founder, challenge weak ideas, and build better businesses.

---

## What Problem It Solves

Most people building startups or side projects lack access to a consistent strategic thinking partner. Roy fills that role — available anytime, remembers previous sessions, and never gives you shallow motivational advice.

---

## How It Works

1. The agent loads its personality from `system_prompt.txt` at startup.
2. It connects to a local SQLite database (`memory.db`) to persist conversation history across sessions.
3. On each turn, it retrieves the last 20 messages from memory and passes them as context to the LLM.
4. When the user says goodbye, Roy detects a `terminate` block in the response and gracefully exits.

**LLM used:** `anthropic/claude-sonnet-4-5` via LiteLLM

---

## External APIs

| Service   | Purpose                  | Key Required |
|-----------|--------------------------|-------------|
| Anthropic | LLM inference via LiteLLM | Yes         |

---

## Environment Variables

| Variable           | Description                              |
|--------------------|------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com |

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Agents.git
cd AI-Agents/entrepreneurship-coach-agent

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

Roy will greet you and load any previous session messages from memory. Type your questions or business ideas and press Enter.

To end the session, say something like `bye`, `goodbye`, or `that's all`.

---

## ⚠️ Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values — it is safe to commit.

---

## Agent Persona

**Name:** Roy  
**Role:** AI Strategy and Entrepreneurship Coach  
**Memory:** Persistent (SQLite — last 20 messages per session)  
**Termination:** Automatic via `terminate` block in LLM response
