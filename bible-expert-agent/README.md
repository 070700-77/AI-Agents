# Yeshúa — Bible Expert Agent

Yeshúa is a respectful, rigorous conversational guide for Bible study. He retrieves exact passages, searches words and phrases, and helps you compare texts and understand themes — always verifying quotes against a Bible API.

---

## What Problem It Solves

Language models often misquote or invent Bible verses. This agent is strictly prohibited from inventing references or quotes: whenever exact text is needed it must call the API, and if the API fails or returns nothing, it must say so instead of improvising. It clearly separates verified text from interpretation.

---

## How It Works

1. The agent loads its personality, rules and tool definitions from `system_prompt.txt`.
2. Conversation history is persisted in a local `memory.db` (SQLite). The last 20 messages are recalled on every start, so the agent remembers earlier sessions.
3. On each user message, the **agentic loop** runs:
   - The LLM decides whether it needs external data.
   - If it does, it answers with an ` ```action ` block containing a `tool_name` and its `args`.
   - The program parses the block, a router calls the matching Bible endpoint, and the result is fed back to the LLM.
   - The loop repeats until the LLM answers in plain text, which is printed to the user.
4. When the user says goodbye, the LLM emits a `terminate` block and the program exits gracefully.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**External API:** [Complete Study Bible](https://rapidapi.com/) via RapidAPI (`complete-study-bible.p.rapidapi.com`)

---

## Available Tools

| Tool                    | Description |
|-------------------------|-------------|
| `verse_range_api`       | Fetch a verse or range of verses from a book/chapter |
| `full_chapter_api`      | Fetch a full chapter |
| `search_all_words_api`  | Search for passages containing all given words |
| `search_exact_phrase_api` | Search for an exact phrase |
| `passage_of_the_day_api` | Get the passage of the day |

---

## External APIs

| Service   | Purpose                  | Key Required |
|-----------|--------------------------|--------------|
| Anthropic | LLM inference via LiteLLM | Yes          |
| Complete Study Bible | Verified Bible text and search | Yes (RapidAPI key) |

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
cd AI-Agents/bible-expert-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env          # Windows: copy .env.example .env
# Open .env and add your ANTHROPIC_API_KEY and X_RAPIDAPI_KEY

# 5. Subscribe to the API on RapidAPI (complete-study-bible) with your key
```

---

## How to Run

```bash
python agent.py
```

Example prompts:

- `Show me John 3:16-21.`
- `Where does the phrase "love your neighbor" appear?`
- `Give me the passage of the day and a short reflection.`

---

## Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values and is safe to commit. The local `memory.db` (your conversation history) is also git-ignored.

---

## Agent Persona

**Name:** Yeshúa  
**Role:** Bible study guide (an AI representation — never presented as divine authority)  
**Language:** Responds in the user's language (Spanish by default)  
**Memory:** Persistent (SQLite — last 20 messages)  
**Termination:** Automatic via `terminate` block in the LLM response
