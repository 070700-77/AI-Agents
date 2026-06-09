# Joshua — Job Seeker Agent 💼

Joshua is a conversational AI agent specialized in helping you find, evaluate, and apply to real-time job opportunities. He searches live job listings, analyzes how well each vacancy fits your profile, and suggests tailored application strategies.

---

## What Problem It Solves

Job searching is time-consuming and generic. Joshua combines live job data from the LinkedIn/JSearch API with LLM-powered fit analysis, so you get ranked opportunities with personalized advice — not just a raw list.

---

## How It Works

1. Joshua loads his personality and your professional profile from `system_prompt.txt`.
2. Conversation history is persisted in `memory.db` (SQLite).
3. When you ask for jobs, the **inner agentic loop** runs:
   - The LLM maps your request to a structured API call (query, location, filters).
   - An ` ```action ` block triggers `access_job_finder_api`.
   - The API returns real-time job listings with details like title, company, location, and apply link.
   - The LLM analyzes fit, ranks opportunities, and provides application guidance.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**Jobs API:** [LinkedIn Data API](https://rapidapi.com/) via RapidAPI

---

## Available Tools

| Tool                    | Description                                                  |
|-------------------------|--------------------------------------------------------------|
| `access_job_finder_api` | Searches real-time job listings with filters and pagination  |

---

## External APIs

| Service             | Purpose                          | Key Required |
|---------------------|----------------------------------|-------------|
| Anthropic           | LLM inference via LiteLLM        | Yes         |
| RapidAPI (LinkedIn) | Real-time job listings           | Yes         |

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
cd AI-Agents/jobseeker-agent

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
- `Find junior data analyst jobs in Bogotá`
- `Search for remote business analyst roles in Colombia`
- `Look for AI strategy positions posted this week`

---

## ⚠️ Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values — it is safe to commit.

---

## Agent Persona

**Name:** Joshua  
**Role:** Real-time job search assistant  
**Memory:** Persistent (SQLite — last 20 messages per session)  
**Termination:** Automatic via `terminate` block in LLM response
