"""Configuration settings for the betting agent."""

# Default thresholds
MIN_EV_THRESHOLD = 0.05  # Minimum expected value to recommend a bet (5%)
MIN_CONFIDENCE = 0.60  # Minimum confidence level (60%)

# Team strength calculation weights
TEAM_STRENGTH_WEIGHTS = {
    'recent_form': 0.35,  # Last 5 games
    'overall_record': 0.25,  # Season record
    'head_to_head': 0.20,  # Historical matchups
    'home_advantage': 0.15,  # Home/away factor
    'injury_impact': 0.05  # Player availability
}

# Odds format preference
PREFERRED_ODDS_FORMAT = 'decimal'  # Options: 'decimal', 'fractional', 'american'

