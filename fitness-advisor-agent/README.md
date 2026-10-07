# Leyla — Fitness Advisor Agent

Leyla is a conversational AI fitness advisor. She helps you understand your body composition, health metrics, caloric needs and fitness goals by calling a specialized health-calculation API instead of guessing numbers from memory.

---

## What Problem It Solves

Online health calculators are scattered, and general-purpose chatbots tend to estimate BMI, calories or body fat from memory — often incorrectly. Leyla is forced by her system prompt to call a dedicated calculation API for every metric, then explains in plain language what the result means and what to do with it.

---

## How It Works

1. The agent loads its personality, rules and tool definitions from `system_prompt.txt`.
2. Conversation history is persisted in a local `memory.db` (SQLite). The last 20 messages are recalled on every start, so the agent remembers earlier sessions.
3. On each user message, the **agentic loop** runs:
   - The LLM decides whether it needs external data.
   - If it does, it answers with an ` ```action ` block containing a `tool_name` and its `args`.
   - The program parses the block, a router calls the matching Health Calculator endpoint, and the result is fed back to the LLM.
   - The loop repeats until the LLM answers in plain text, which is printed to the user.
4. When the user says goodbye, the LLM emits a `terminate` block and the program exits gracefully.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**External API:** [Health Calculator API](https://rapidapi.com/) via RapidAPI (`health-calculator-api.p.rapidapi.com`)

---

## Available Tools

| Tool (endpoint) | Description |
|-----------------|-------------|
| `ibw`   | Ideal body weight (Hamwi, Devine, Robinson, Miller) |
| `abw`   | Adjusted body weight |
| `bmi`   | Body mass index |
| `bmr`   | Basal metabolic rate |
| `tdee`  | Total daily energy expenditure |
| `dcn`   | Daily calorie needs for a goal |
| `eer`   | Estimated energy requirement |
| `body-fat` | Body fat percentage |
| `bai`   | Body adiposity index |
| `absi`  | A Body Shape Index |
| `bfs`   | Body frame size |
| `ffmi`  | Fat-free mass index |
| `thr`   | Target heart rate zones |
| `dwi`   | Daily water intake |
| `eag`   | Estimated average glucose |

---

## External APIs

| Service   | Purpose                  | Key Required |
|-----------|--------------------------|--------------|
| Anthropic | LLM inference via LiteLLM | Yes          |
| Health Calculator API | Health and body-composition calculations | Yes (RapidAPI key) |

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
cd AI-Agents/fitness-advisor-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env          # Windows: copy .env.example .env
# Open .env and add your ANTHROPIC_API_KEY and X_RAPIDAPI_KEY

# 5. Subscribe to the API on RapidAPI (health-calculator-api) with your key
```

---

## How to Run

```bash
python agent.py
```

Example prompts:

- `I'm 28, male, 178 cm and 80 kg. What's my BMI and daily calorie needs to lose weight?`
- `Calculate my target heart rate zones for cardio.`
- `How much water should I drink per day if I train 5 times a week?`

---

## Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values and is safe to commit. The local `memory.db` (your conversation history) is also git-ignored.

---

## Agent Persona

**Name:** Leyla  
**Role:** Warm, science-backed fitness advisor  
**Language:** English  
**Memory:** Persistent (SQLite — last 20 messages)  
**Termination:** Automatic via `terminate` block in the LLM response
