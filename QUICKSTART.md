# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Google Gemini API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create or copy your API key

3. **Set environment variable:**
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```
   
   Or create a `.env` file:
   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

## Quick Test

```python
from betting_agent import BettingAgent

agent = BettingAgent()
result = agent.analyze_match(
    team1="Team A",
    team2="Team B",
    team1_odds=2.5,
    team2_odds=1.8
)

print(result["recommendation"])
```

## CLI Example

```bash
python main.py --team1 "Manchester United" --team2 "Liverpool" --odds1 2.5 --odds2 1.8 --draw 3.2
```

## What the Agent Does

1. Takes team names and betting odds as input
2. Optionally accepts team statistics (form, records, etc.)
3. Uses Gemini LLM to dynamically analyze:
   - Team strength comparison
   - Odds vs. expected probabilities
   - Value bet opportunities
4. Returns betting recommendations with reasoning

That's it! The agent uses LLM reasoning to make dynamic betting decisions based on the data you provide.

