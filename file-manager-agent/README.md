# Koda — File Manager Agent 🗂️

Koda is a conversational AI agent with access to file system tools. It can list files in the current directory, read their contents, and count words — all driven by natural language instructions.

---

## What Problem It Solves

Instead of manually navigating directories and opening files, you simply ask Koda in plain English. It decides which tool to call, executes it, and reports back — demonstrating a basic agentic loop with real tool use.

---

## How It Works

1. Koda loads its personality from `system_prompt.txt` at startup.
2. Conversation history is persisted in `memory.db` (SQLite).
3. On each turn, an **inner agentic loop** runs:
   - The LLM receives the conversation and decides whether to call a tool or give a final answer.
   - If the response contains an ` ```action ` block, the matching Python function is executed.
   - The tool result is fed back to the LLM, which continues reasoning.
   - The loop exits when the LLM produces a plain response (no action block).
4. When the user ends the session, a `terminate` block signals exit.

**LLM used:** `anthropic/claude-sonnet-4-5` via LiteLLM

---

## Available Tools

| Tool         | Description                                          |
|--------------|------------------------------------------------------|
| `list_files` | Lists all files and folders in the working directory |
| `read_file`  | Reads the full content of a specified file           |
| `word_count` | Counts the words in a specified file                 |

---

## External APIs

| Service   | Purpose                  | Key Required |
|-----------|--------------------------|-------------|
| Anthropic | LLM inference via LiteLLM | Yes         |

---

## Environment Variables

| Variable            | Description                                        |
|---------------------|----------------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com  |

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Agents.git
cd AI-Agents/file-manager-agent

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
- `What files are in this folder?`
- `Read the file notes.txt`
- `How many words does report.md have?`

---

## ⚠️ Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values — it is safe to commit.

---

## Agent Persona

**Name:** Koda  
**Role:** File system assistant  
**Memory:** Persistent (SQLite — last 20 messages per session)  
**Termination:** Automatic via `terminate` block in LLM response
