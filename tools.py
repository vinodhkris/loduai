"""Custom LangChain tools for betting analysis."""

from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class TeamStrengthInput(BaseModel):
    """Input schema for team strength analysis."""
    team1: str = Field(description="Name of the first team")
    team2: str = Field(description="Name of the second team")
    team1_recent_form: Optional[str] = Field(None, description="Recent form for team1 (e.g., 'WWLWD')")
    team2_recent_form: Optional[str] = Field(None, description="Recent form for team2 (e.g., 'WLWWL')")
    team1_record: Optional[str] = Field(None, description="Season record for team1 (e.g., '15W-5L-3D')")
    team2_record: Optional[str] = Field(None, description="Season record for team2 (e.g., '12W-8L-3D')")
    head_to_head: Optional[str] = Field(None, description="Head to head record (e.g., 'Team1: 3 wins, Team2: 2 wins')")
    home_team: Optional[str] = Field(None, description="Name of the home team")
    additional_context: Optional[str] = Field(None, description="Any additional context about the teams")


class TeamStrengthTool(BaseTool):
    """Tool to analyze team strength based on various metrics."""
    
    name = "analyze_team_strength"
    description = """Analyzes and compares the strength of two teams based on:
    - Recent form (last 5 games)
    - Overall season record
    - Head-to-head history
    - Home/away advantage
    - Additional context provided
    
    Returns a dictionary with strength scores and analysis."""
    
    args_schema = TeamStrengthInput
    
    def _run(
        self,
        team1: str,
        team2: str,
        team1_recent_form: Optional[str] = None,
        team2_recent_form: Optional[str] = None,
        team1_record: Optional[str] = None,
        team2_record: Optional[str] = None,
        head_to_head: Optional[str] = None,
        home_team: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> str:
        """Analyze team strength."""
        analysis = {
            "team1": team1,
            "team2": team2,
            "team1_strength_score": 0.5,
            "team2_strength_score": 0.5,
            "analysis": "Based on provided data",
            "factors_considered": []
        }
        
        # Simple scoring logic (can be enhanced)
        team1_score = 0.5
        team2_score = 0.5
        factors = []
        
        if team1_recent_form:
            team1_wins = team1_recent_form.upper().count('W')
            team1_form_score = team1_wins / len(team1_recent_form) if team1_recent_form else 0.5
            team1_score += team1_form_score * 0.2
            factors.append(f"Team1 recent form: {team1_recent_form}")
        
        if team2_recent_form:
            team2_wins = team2_recent_form.upper().count('W')
            team2_form_score = team2_wins / len(team2_recent_form) if team2_recent_form else 0.5
            team2_score += team2_form_score * 0.2
            factors.append(f"Team2 recent form: {team2_recent_form}")
        
        if home_team:
            if home_team.lower() == team1.lower():
                team1_score += 0.1
                factors.append(f"{team1} has home advantage")
            elif home_team.lower() == team2.lower():
                team2_score += 0.1
                factors.append(f"{team2} has home advantage")
        
        if head_to_head:
            factors.append(f"Head-to-head: {head_to_head}")
        
        if additional_context:
            factors.append(f"Additional context: {additional_context}")
        
        # Normalize scores to sum to 1.0
        total = team1_score + team2_score
        if total > 0:
            team1_score = team1_score / total
            team2_score = team2_score / total
        
        analysis["team1_strength_score"] = round(team1_score, 3)
        analysis["team2_strength_score"] = round(team2_score, 3)
        analysis["factors_considered"] = factors
        
        return f"""Team Strength Analysis:
Team1 ({team1}): {team1_score:.1%} win probability
Team2 ({team2}): {team2_score:.1%} win probability
Factors considered: {', '.join(factors) if factors else 'Limited data available'}"""


class OddsAnalysisInput(BaseModel):
    """Input schema for odds analysis."""
    team1_odds: float = Field(description="Decimal odds for team1 to win")
    team2_odds: float = Field(description="Decimal odds for team2 to win")
    draw_odds: Optional[float] = Field(None, description="Decimal odds for draw")
    team1_strength: float = Field(description="Team1 strength score (0-1)")
    team2_strength: float = Field(description="Team2 strength score (0-1)")


class OddsAnalysisTool(BaseTool):
    """Tool to analyze odds and calculate expected value."""
    
    name = "analyze_odds_value"
    description = """Analyzes betting odds and calculates expected value based on team strength.
    Converts decimal odds to implied probabilities and compares with actual probabilities.
    Returns value bet recommendations."""
    
    args_schema = OddsAnalysisInput
    
    def _run(
        self,
        team1_odds: float,
        team2_odds: float,
        draw_odds: Optional[float] = None,
        team1_strength: float = 0.5,
        team2_strength: float = 0.5,
    ) -> str:
        """Analyze odds and calculate expected value."""
        
        # Convert odds to implied probabilities
        team1_implied_prob = 1.0 / team1_odds if team1_odds > 0 else 0
        team2_implied_prob = 1.0 / team2_odds if team2_odds > 0 else 0
        draw_implied_prob = 1.0 / draw_odds if draw_odds and draw_odds > 0 else 0
        
        # Normalize strength scores
        total_strength = team1_strength + team2_strength
        if total_strength > 0:
            team1_actual_prob = team1_strength / total_strength
            team2_actual_prob = team2_strength / total_strength
        else:
            team1_actual_prob = 0.5
            team2_actual_prob = 0.5
        
        # Handle draw probability
        if draw_odds:
            # Adjust for draw (simplified model)
            draw_actual_prob = 0.1  # Default 10% draw probability
            remaining_prob = 0.9
            team1_actual_prob = team1_actual_prob * remaining_prob
            team2_actual_prob = team2_actual_prob * remaining_prob
        else:
            draw_actual_prob = 0
            draw_implied_prob = 0
        
        # Calculate Expected Value (EV)
        # EV = (Actual Probability × Odds) - 1
        team1_ev = (team1_actual_prob * team1_odds) - 1
        team2_ev = (team2_actual_prob * team2_odds) - 1
        draw_ev = (draw_actual_prob * draw_odds) - 1 if draw_odds else 0
        
        # Find value bets (positive EV)
        recommendations = []
        if team1_ev > 0.05:
            recommendations.append(f"Team1 bet: EV = {team1_ev:.1%}, Odds = {team1_odds}, Implied prob = {team1_implied_prob:.1%}, Actual prob = {team1_actual_prob:.1%}")
        if team2_ev > 0.05:
            recommendations.append(f"Team2 bet: EV = {team2_ev:.1%}, Odds = {team2_odds}, Implied prob = {team2_implied_prob:.1%}, Actual prob = {team2_actual_prob:.1%}")
        if draw_ev > 0.05 and draw_odds:
            recommendations.append(f"Draw bet: EV = {draw_ev:.1%}, Odds = {draw_odds}, Implied prob = {draw_implied_prob:.1%}, Actual prob = {draw_actual_prob:.1%}")
        
        result = f"""Odds Analysis:
Team1: Odds {team1_odds} → Implied prob {team1_implied_prob:.1%}, Actual prob {team1_actual_prob:.1%}, EV = {team1_ev:.1%}
Team2: Odds {team2_odds} → Implied prob {team2_implied_prob:.1%}, Actual prob {team2_actual_prob:.1%}, EV = {team2_ev:.1%}"""
        
        if draw_odds:
            result += f"\nDraw: Odds {draw_odds} → Implied prob {draw_implied_prob:.1%}, Actual prob {draw_actual_prob:.1%}, EV = {draw_ev:.1%}"
        
        if recommendations:
            result += f"\n\nValue Bet Recommendations:\n" + "\n".join(f"- {rec}" for rec in recommendations)
        else:
            result += "\n\nNo significant value bets identified (EV < 5%)"
        
        return result


def get_all_tools():
    """Return all available tools."""
    return [TeamStrengthTool(), OddsAnalysisTool()]

