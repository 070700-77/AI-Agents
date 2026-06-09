# Valya — Flight Finder Agent ✈️

Valya is a conversational AI agent that searches for real-time flights, compares prices, retrieves booking options, and helps you find the best travel deals — all through natural language.

---

## What Problem It Solves

Finding and comparing flights across multiple carriers is tedious. Valya acts as a personal travel assistant: you describe your trip in plain English and she handles the API calls, parses the results, and presents the best options with prices, stops, duration, and booking links.

---

## How It Works

1. Valya loads her personality from `system_prompt.txt` at startup.
2. Conversation history is persisted in `memory.db` (SQLite).
3. The **inner agentic loop** translates your request into specific Google Flights API calls:
   - ` ```action ` blocks trigger the appropriate function via the `router`.
   - Results include flight details, prices, airline, aircraft, carbon emissions, and tokens for pagination.
   - The LLM presents options clearly and can chain multiple tool calls (search → book → URL).
4. Rate limit protection is built in — if the API throttles, Valya waits 60 seconds and retries automatically.

**LLM used:** `anthropic/claude-sonnet-4-6` via LiteLLM  
**Flights API:** [Google Flights](https://rapidapi.com/apiheya/api/google-flights2) via RapidAPI

---

## Available Tools

| Tool                 | Description                                                     |
|----------------------|-----------------------------------------------------------------|
| `search_flights`     | Search available flights by origin, destination, date           |
| `get_booking_details`| Get booking options (airlines/sites) for a specific flight      |
| `get_booking_url`    | Get the direct booking URL for a selected option                |
| `search_airport`     | Search for airport codes by city or airport name                |
| `get_calendar_picker`| Find the cheapest travel dates in a date range                  |
| `get_next_flights`   | Load more results using a pagination token                      |
| `get_price_graph`    | View price trends across a range of departure dates             |
| `get_calendar_grid`  | Grid view of prices for combinations of outbound/return dates   |

---

## External APIs

| Service                | Purpose                          | Key Required |
|------------------------|----------------------------------|-------------|
| Anthropic              | LLM inference via LiteLLM        | Yes         |
| RapidAPI (G. Flights)  | Real-time flight search          | Yes         |

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
cd AI-Agents/flight-finder-agent

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
- `Find flights from Bogotá to Madrid in July`
- `Search for the cheapest dates to fly BOG to JFK in August`
- `Show me economy flights from MED to NYC for 2 adults on July 15`
- `Get booking options for that flight`

---

## ⚠️ Security Warning

**Never commit your `.env` file to GitHub.**

Your real credentials must live only in `.env`, which is already listed in `.gitignore`. The `.env.example` file contains only placeholder values — it is safe to commit.

---

## Agent Persona

**Name:** Valya  
**Role:** AI travel and flight booking assistant  
**Memory:** Persistent (SQLite — last 6 messages per session)  
**Termination:** Automatic via `terminate` block in LLM response
