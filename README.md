# LangChain Game Betting Agent

An intelligent betting agent built with LangChain and Google Gemini that analyzes team strength and identifies betting opportunities based on odds mismatches.

## Features

- **LLM-Powered Dynamic Analysis**: Uses Google Gemini API for intelligent, context-aware reasoning
- **Team Strength Analysis**: Evaluates team performance using multiple metrics
- **Odds Comparison**: Compares betting odds with calculated probabilities
- **Value Bet Detection**: Identifies bets where odds don't match expected probabilities
- **Expected Value Calculation**: Calculates EV to make informed betting decisions
- **LangChain Agent Framework**: Uses LangChain's agent framework with custom tools

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd loduai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
# Get your API key from: https://makersuite.google.com/app/apikey
```

## Usage

### Basic Usage (Python)

```python
from betting_agent import BettingAgent

# Initialize the agent
agent = BettingAgent()

# Analyze a match with minimal data
result = agent.analyze_match(
    team1="Manchester United",
    team2="Liverpool",
    team1_odds=2.5,
    team2_odds=1.8,
    draw_odds=3.2
)

print(result["recommendation"])
print(result["analysis"])
```

### Advanced Usage with Team Data

```python
from betting_agent import BettingAgent

agent = BettingAgent(model_name="gemini-pro", temperature=0.3)

result = agent.analyze_match(
    team1="Barcelona",
    team2="Real Madrid",
    team1_odds=2.1,
    team2_odds=1.9,
    draw_odds=3.5,
    team1_recent_form="WWLWW",  # W=Win, L=Loss, D=Draw
    team2_recent_form="WLWWL",
    team1_record="20W-5L-3D",
    team2_record="18W-7L-3D",
    head_to_head="Barcelona: 5 wins, Real Madrid: 3 wins, Draws: 2",
    home_team="Barcelona",
    additional_context="Barcelona has key players returning from injury"
)

print(f"Recommendation: {result['recommendation']}")
print(f"Confidence: {result.get('confidence', 0):.1%}")
print(f"Expected Value: {result.get('expected_value', 0):.1%}")
```

### Using the CLI

```bash
# Basic usage
python main.py --team1 "Chicago Bears" --team2 "SF 49ers" --odds1 2.5 --odds2 1.8 --draw 3.2

# With additional data
python main.py \
  --team1 "Chicago Bears" \
  --team2 "Liverpool" \
  --odds1 2.5 \
  --odds2 1.8 \
  --draw 3.2 \
  --form1 "WWLWD" \
  --form2 "WLWWL" \
  --record1 "15W-5L-3D" \
  --record2 "12W-8L-3D" \
  --home "Manchester United" \
  --h2h "Man Utd: 3 wins, Liverpool: 2 wins"

# JSON output
python main.py --team1 "Team A" --team2 "Team B" --odds1 2.5 --odds2 1.8 --output json
```

### Run Example

```bash
python example.py
```

## Architecture

The agent uses LangChain's agent framework with Gemini API and custom tools:

1. **LLM-Powered Analysis**: Uses Google Gemini for dynamic, context-aware analysis
2. **Team Strength Analyzer Tool**: Analyzes historical performance, recent form, head-to-head records
3. **Odds Analysis Tool**: Compares odds with expected probabilities and calculates expected value
4. **Dynamic Reasoning**: The LLM dynamically reasons about team strength and odds mismatches
5. **Value Bet Detection**: Identifies betting opportunities where odds don't match team strength

### How It Works

1. **Input**: The `analyze_match` method accepts match details, odds, and optional team data
2. **LLM Processing**: A dynamic prompt is built and sent to the Gemini LLM via LangChain agent
3. **Tool Usage**: The agent uses custom tools to:
   - Analyze team strength based on provided metrics
   - Calculate expected value by comparing odds with probabilities
4. **Output**: Returns structured recommendations with reasoning, confidence, and expected value

## Configuration

Edit `config.py` to customize:
- `MIN_EV_THRESHOLD`: Minimum expected value to recommend a bet (default: 5%)
- `MIN_CONFIDENCE`: Minimum confidence level (default: 60%)
- `TEAM_STRENGTH_WEIGHTS`: Weights for different factors in team strength calculation

## Project Structure

```
loduai/
├── betting_agent.py      # Main agent class with Gemini integration
├── tools.py              # Custom LangChain tools (team strength, odds analysis)
├── config.py             # Configuration settings
├── main.py               # CLI interface
├── example.py            # Example usage script
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .env.example         # Environment variables template
```

## API Reference

### BettingAgent Class

#### `__init__(model_name="gemini-pro", temperature=0.3)`
Initialize the betting agent.

- `model_name`: Gemini model name (default: "gemini-pro")
- `temperature`: Model temperature 0-1 (lower = more deterministic)

#### `analyze_match(...)`
Analyze a match and return betting recommendations.

**Required Parameters:**
- `team1`: Name of team 1
- `team2`: Name of team 2
- `team1_odds`: Decimal odds for team1 to win
- `team2_odds`: Decimal odds for team2 to win

**Optional Parameters:**
- `draw_odds`: Decimal odds for draw
- `team1_recent_form`: Recent form (e.g., "WWLWD")
- `team2_recent_form`: Recent form
- `team1_record`: Season record (e.g., "15W-5L-3D")
- `team2_record`: Season record
- `head_to_head`: Head-to-head history
- `home_team`: Name of home team
- `additional_context`: Any additional context

**Returns:** Dictionary with:
- `recommendation`: Betting recommendation
- `analysis`: Detailed analysis text
- `confidence`: Confidence level (0-1)
- `expected_value`: Expected value (0-1)
- Match details and odds

## Disclaimer

This is an educational project. Always gamble responsibly and within your means. Past performance does not guarantee future results. This agent is for informational purposes only and does not guarantee betting success.
