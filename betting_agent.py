"""LangChain betting agent using Gemini API."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json

from tools import get_all_tools
from config import MIN_EV_THRESHOLD, MIN_CONFIDENCE

load_dotenv()


class BettingAgent:
    """LangChain agent for analyzing game bets using Gemini."""
    
    def __init__(self, model_name: str = "gemini-pro", temperature: float = 0.3):
        """
        Initialize the betting agent.
        
        Args:
            model_name: Gemini model name (default: "gemini-pro")
            temperature: Model temperature for creativity (0-1, lower = more deterministic)
        """
        # ChatGoogleGenerativeAI reads GOOGLE_API_KEY from environment automatically
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please set it in your .env file or export it as an environment variable."
            )
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
        )
        
        # Get tools
        self.tools = get_all_tools()
        
        # Store chat history manually (simpler approach for new API)
        self.chat_history = []
        
        # Create system prompt for the agent
        system_prompt = SystemMessage(content="""You are a helpful assistant that analyzes betting opportunities.
You have access to tools that can analyze team strength and odds value.
Use these tools to provide comprehensive betting recommendations.

When analyzing a match:
1. First use the analyze_team_strength tool to evaluate team strengths
2. Then use the analyze_odds_value tool to compare odds with probabilities
3. Provide a clear recommendation with reasoning""")
        
        # Create agent using the modern LangChain 1.2.0 API
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
            debug=True,
        )
    
    def analyze_match(
        self,
        team1: str,
        team2: str,
        team1_odds: float,
        team2_odds: float,
        draw_odds: Optional[float] = None,
        team1_recent_form: Optional[str] = None,
        team2_recent_form: Optional[str] = None,
        team1_record: Optional[str] = None,
        team2_record: Optional[str] = None,
        head_to_head: Optional[str] = None,
        home_team: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dynamically analyze a match using LLM-powered reasoning.
        
        Args:
            team1: Name of team 1
            team2: Name of team 2
            team1_odds: Decimal odds for team1 to win
            team2_odds: Decimal odds for team2 to win
            draw_odds: Optional decimal odds for draw
            team1_recent_form: Recent form for team1 (e.g., "WWLWD")
            team2_recent_form: Recent form for team2
            team1_record: Season record for team1 (e.g., "15W-5L-3D")
            team2_record: Season record for team2
            head_to_head: Head to head history
            home_team: Name of home team
            additional_context: Any additional context
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        
        # Build dynamic prompt for the LLM
        prompt = self._build_analysis_prompt(
            team1=team1,
            team2=team2,
            team1_odds=team1_odds,
            team2_odds=team2_odds,
            draw_odds=draw_odds,
            team1_recent_form=team1_recent_form,
            team2_recent_form=team2_recent_form,
            team1_record=team1_record,
            team2_record=team2_record,
            head_to_head=head_to_head,
            home_team=home_team,
            additional_context=additional_context,
        )
        
        try:
            # Use the agent to analyze
            # The new create_agent API returns a state graph that expects messages
            
            # Invoke the agent with messages (include chat history)
            result_dict = self.agent.invoke({
                "messages": self.chat_history + [HumanMessage(content=prompt)]
            })
            
            # Extract the output from the response
            # The new API returns messages in the state
            response = ""
            if isinstance(result_dict, dict):
                if "messages" in result_dict:
                    # Get the last AI message
                    messages = result_dict["messages"]
                    ai_messages = [m for m in messages if hasattr(m, 'content') and m.content]
                    if ai_messages:
                        response = ai_messages[-1].content
                    else:
                        response = str(result_dict)
                    # Update chat history with all messages
                    self.chat_history = messages
                elif "output" in result_dict:
                    response = result_dict["output"]
                    # Update chat history
                    self.chat_history.append(HumanMessage(content=prompt))
                    self.chat_history.append(AIMessage(content=response))
                else:
                    response = str(result_dict)
            else:
                response = str(result_dict)
            
            # Parse and structure the response
            result = self._parse_response(
                response=response,
                team1=team1,
                team2=team2,
                team1_odds=team1_odds,
                team2_odds=team2_odds,
                draw_odds=draw_odds,
            )
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "team1": team1,
                "team2": team2,
                "recommendation": "Unable to complete analysis due to error"
            }
    
    def _build_analysis_prompt(
        self,
        team1: str,
        team2: str,
        team1_odds: float,
        team2_odds: float,
        draw_odds: Optional[float],
        team1_recent_form: Optional[str],
        team2_recent_form: Optional[str],
        team1_record: Optional[str],
        team2_record: Optional[str],
        head_to_head: Optional[str],
        home_team: Optional[str],
        additional_context: Optional[str],
    ) -> str:
        """Build a comprehensive prompt for the LLM agent."""
        
        prompt = f"""Analyze the following betting opportunity and provide a comprehensive recommendation.

MATCH DETAILS:
- Team 1: {team1}
- Team 2: {team2}
- Team 1 Odds: {team1_odds}
- Team 2 Odds: {team2_odds}
"""
        
        if draw_odds:
            prompt += f"- Draw Odds: {draw_odds}\n"
        
        if home_team:
            prompt += f"- Home Team: {home_team}\n"
        
        prompt += "\nTEAM DATA:\n"
        
        if team1_recent_form:
            prompt += f"- {team1} recent form: {team1_recent_form}\n"
        if team2_recent_form:
            prompt += f"- {team2} recent form: {team2_recent_form}\n"
        if team1_record:
            prompt += f"- {team1} season record: {team1_record}\n"
        if team2_record:
            prompt += f"- {team2} season record: {team2_record}\n"
        if head_to_head:
            prompt += f"- Head-to-head: {head_to_head}\n"
        if additional_context:
            prompt += f"- Additional context: {additional_context}\n"
        
        prompt += f"""
TASK:
1. Use the analyze_team_strength tool to evaluate team strengths based on the provided data
2. Use the analyze_odds_value tool to compare odds with expected probabilities and identify value bets
3. Provide a clear recommendation on whether there's a betting opportunity
4. Consider odds mismatches - when the bookmaker's odds don't align with the actual team strength
5. Calculate expected value and only recommend bets with positive EV above {MIN_EV_THRESHOLD*100}%

Please provide:
- A clear recommendation (bet on Team1, Team2, Draw, or no bet)
- Expected value calculation
- Confidence level
- Reasoning for your decision
- Any risks or considerations

Format your response as a structured analysis."""
        
        return prompt
    
    def _parse_response(
        self,
        response: str,
        team1: str,
        team2: str,
        team1_odds: float,
        team2_odds: float,
        draw_odds: Optional[float],
    ) -> Dict[str, Any]:
        """Parse the LLM response into a structured format."""
        
        # Try to extract structured information from the response
        result = {
            "team1": team1,
            "team2": team2,
            "team1_odds": team1_odds,
            "team2_odds": team2_odds,
            "draw_odds": draw_odds,
            "analysis": response,
            "recommendation": "Review the analysis",
            "confidence": 0.0,
            "expected_value": 0.0,
        }
        
        # Simple parsing to extract key information (can be enhanced)
        response_lower = response.lower()
        
        # Extract recommendation
        if "bet on team1" in response_lower or f"bet on {team1.lower()}" in response_lower:
            result["recommendation"] = f"Bet on {team1}"
        elif "bet on team2" in response_lower or f"bet on {team2.lower()}" in response_lower:
            result["recommendation"] = f"Bet on {team2}"
        elif "bet on draw" in response_lower or "draw" in response_lower and "bet" in response_lower:
            result["recommendation"] = "Bet on Draw"
        elif "no bet" in response_lower or "avoid" in response_lower or "not recommend" in response_lower:
            result["recommendation"] = "No bet recommended"
        
        # Try to extract confidence and EV from response
        import re
        ev_pattern = r'ev[:\s=]+([\d.]+)%?'
        conf_pattern = r'confidence[:\s=]+([\d.]+)%?'
        
        ev_match = re.search(ev_pattern, response_lower)
        if ev_match:
            try:
                result["expected_value"] = float(ev_match.group(1)) / 100.0
            except:
                pass
        
        conf_match = re.search(conf_pattern, response_lower)
        if conf_match:
            try:
                result["confidence"] = float(conf_match.group(1)) / 100.0
            except:
                pass
        
        return result
    
    def clear_memory(self):
        """Clear the conversation memory."""
        self.chat_history = []

