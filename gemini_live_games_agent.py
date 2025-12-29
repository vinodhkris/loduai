"""Agent that uses Gemini to fetch live NBA and NFL games and provide detailed analysis.

This agent uses Google Gemini to:
1. Fetch all currently live NBA and NFL games
2. Get complete game details (scores, odds, team stats, etc.)
3. Analyze each game with betting recommendations
4. Provide detailed analysis for each live game

Usage:
    python gemini_live_games_agent.py

Requirements:
    - GOOGLE_API_KEY in environment or .env file
    - All dependencies from requirements.txt

Best Results:
    - Run during NBA game hours (evenings, 7 PM - 11 PM EST)
    - Run during NFL game hours (Sunday afternoons/evenings, Monday nights)
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from betting_agent import BettingAgent
from tools import get_all_tools
from langchain.agents import create_agent


class GeminiLiveGamesAgent:
    """Agent that uses Gemini to fetch and analyze live NBA and NFL games."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        """
        Initialize the Gemini Live Games Agent.
        
        Args:
            model_name: Gemini model name (default: "gemini-2.5-flash")
            temperature: Model temperature (0-1, lower = more deterministic)
        """
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
        
        # Initialize betting agent for analysis
        self.betting_agent = BettingAgent(model_name=model_name, temperature=temperature)
        
        # Get tools for analysis
        self.tools = get_all_tools()
        
        # Create agent with tools
        system_prompt = SystemMessage(content="""You are an expert sports analyst and betting advisor.
You have access to real-time sports information and can analyze betting opportunities.
Use the available tools to analyze team strength and odds value.
Provide comprehensive, detailed analysis with clear recommendations.""")
        
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
            debug=False,
        )
    
    def fetch_live_games_from_gemini(self) -> List[Dict[str, Any]]:
        """
        Use Gemini to fetch all currently live NBA and NFL games.
        Returns a list of game dictionaries with all details.
        """
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        
        prompt = f"""You are a sports data expert with access to real-time game information. You have knowledge of current NBA and NFL schedules, live scores, and betting odds.

TASK: Find ALL games that are currently LIVE (in progress) right now. 

Current date and time: {current_date}
"""

        try:
            # Use Gemini to fetch live games
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Extract content
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse JSON from response
            # Sometimes Gemini includes markdown code blocks or extra text
            content = content.strip()
            
            # Remove markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Try to find JSON array in the response
            import re
            # Look for JSON array pattern
            json_match = re.search(r'(\[[\s\S]*\])', content)
            if json_match:
                content = json_match.group(1)
            
            # Parse JSON
            try:
                games = json.loads(content)
                if not isinstance(games, list):
                    print(f"⚠️  Response is not a list, got: {type(games)}")
                    games = []
            except json.JSONDecodeError as e:
                print(f"⚠️  Error parsing JSON from Gemini: {e}")
                print(f"Attempting to extract JSON from response...")
                # Try more aggressive extraction
                json_match = re.search(r'(\[[\s\S]{10,}\])', content)
                if json_match:
                    try:
                        games = json.loads(json_match.group(1))
                        print("✅ Successfully extracted JSON")
                    except:
                        print(f"⚠️  Could not parse extracted JSON")
                        print(f"First 500 chars of response: {content[:500]}...")
                        games = []
                else:
                    print(f"⚠️  No JSON array found in response")
                    print(f"First 500 chars: {content[:500]}...")
                    games = []
            
            return games
            
        except Exception as e:
            print(f"❌ Error fetching live games from Gemini: {e}")
            return []
    
    def analyze_game_with_details(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single game with all available details using the betting agent.
        """
        try:
            # Extract game information
            team1 = game.get("team1", "")
            team2 = game.get("team2", "")
            team1_odds = game.get("team1_odds", 2.0)
            team2_odds = game.get("team2_odds", 2.0)
            draw_odds = game.get("draw_odds")
            home_team = game.get("home_team")
            team1_form = game.get("team1_recent_form")
            team2_form = game.get("team2_recent_form")
            team1_record = game.get("team1_record")
            team2_record = game.get("team2_record")
            head_to_head = game.get("head_to_head")
            key_context = game.get("key_context")
            current_score = game.get("current_score")
            game_status = game.get("game_status")
            
            # Build additional context
            additional_context = f"Current Score: {current_score}. Game Status: {game_status}."
            if key_context:
                additional_context += f" {key_context}"
            
            # Analyze using betting agent
            result = self.betting_agent.analyze_match(
                team1=team1,
                team2=team2,
                team1_odds=team1_odds,
                team2_odds=team2_odds,
                draw_odds=draw_odds,
                team1_recent_form=team1_form,
                team2_recent_form=team2_form,
                team1_record=team1_record,
                team2_record=team2_record,
                head_to_head=head_to_head,
                home_team=home_team,
                additional_context=additional_context,
            )
            
            # Add game details to result
            result["sport"] = game.get("sport", "Unknown")
            result["current_score"] = current_score
            result["game_status"] = game_status
            result["game_time"] = game.get("game_time")
            result["key_context"] = key_context
            result["status"] = "LIVE"
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "team1": game.get("team1", "Unknown"),
                "team2": game.get("team2", "Unknown"),
                "status": "LIVE"
            }
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Main method: Fetch all live games and provide comprehensive analysis.
        """
        print("\n" + "="*80)
        print("🏀🏈 GEMINI LIVE GAMES AGENT - NBA & NFL Analysis")
        print("="*80)
        print(f"\n⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🔍 Fetching live games from Gemini...")
        print("   (This may take a moment as Gemini gathers real-time game data)\n")
        
        # Fetch live games using Gemini
        live_games = self.fetch_live_games_from_gemini()
        
        if not live_games:
            print("⚠️  No live games found at this time.")
            print("\nThis could mean:")
            print("  • No NBA or NFL games are currently in progress")
            print("  • Games may have just ended or haven't started yet")
            print("  • Try again during game hours (evenings/weekends)")
            return {
                "timestamp": datetime.now().isoformat(),
                "live_games_count": 0,
                "games": [],
                "summary": "No live games found"
            }
        
        print(f"✅ Found {len(live_games)} live game(s)\n")
        print("="*80)
        
        analyzed_games = []
        
        # Analyze each game
        for idx, game in enumerate(live_games, 1):
            sport_emoji = "🏀" if game.get("sport") == "NBA" else "🏈"
            print(f"\n{'='*80}")
            print(f"{sport_emoji} GAME {idx}/{len(live_games)}: {game.get('team1')} vs {game.get('team2')}")
            print(f"{'='*80}")
            print(f"Sport: {game.get('sport', 'Unknown')}")
            print(f"Home Team: {game.get('home_team', 'N/A')}")
            
            if game.get('current_score'):
                print(f"Current Score: {game.get('current_score')}")
            if game.get('game_status'):
                print(f"Game Status: {game.get('game_status')}")
            
            print(f"\nBetting Odds:")
            print(f"  {game.get('team1')}: {game.get('team1_odds', 'N/A')}")
            print(f"  {game.get('team2')}: {game.get('team2_odds', 'N/A')}")
            if game.get('draw_odds'):
                print(f"  Draw/Tie: {game.get('draw_odds')}")
            
            if game.get('team1_record'):
                print(f"\nSeason Records:")
                print(f"  {game.get('team1')}: {game.get('team1_record')}")
                print(f"  {game.get('team2')}: {game.get('team2_record')}")
            
            if game.get('team1_recent_form'):
                print(f"\nRecent Form:")
                print(f"  {game.get('team1')}: {game.get('team1_recent_form')}")
                print(f"  {game.get('team2')}: {game.get('team2_recent_form')}")
            
            if game.get('key_context'):
                print(f"\nKey Context: {game.get('key_context')}")
            
            print(f"\n{'─'*80}")
            print("📊 ANALYZING GAME...")
            print(f"{'─'*80}\n")
            
            # Analyze the game
            analysis = self.analyze_game_with_details(game)
            analyzed_games.append(analysis)
            
            # Display analysis results
            print(f"\n{'─'*80}")
            print("📊 ANALYSIS RESULTS")
            print(f"{'─'*80}")
            print(f"\n🎯 Recommendation: {analysis.get('recommendation', 'N/A')}")
            
            if analysis.get('confidence'):
                confidence = analysis.get('confidence', 0)
                print(f"📈 Confidence: {confidence:.1%}")
            
            if analysis.get('expected_value'):
                ev = analysis.get('expected_value', 0)
                ev_display = f"{ev:+.1%}" if ev != 0 else "0.0%"
                print(f"💰 Expected Value: {ev_display}")
            
            print(f"\n📝 Detailed Analysis:")
            print(f"{'─'*80}")
            detailed_analysis = analysis.get('analysis', 'No analysis available')
            for line in detailed_analysis.split('\n'):
                if line.strip():
                    print(f"  {line}")
            
            print(f"\n{'─'*80}")
        
        # Generate summary
        summary = self._generate_summary(analyzed_games)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "live_games_count": len(analyzed_games),
            "games": analyzed_games,
            "summary": summary
        }
        
        # Print summary
        print("\n" + "="*80)
        print("📋 SUMMARY REPORT")
        print("="*80)
        print(summary)
        print("="*80)
        
        # Save to file
        output_file = f"gemini_live_games_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Full analysis saved to: {output_file}")
        
        return result
    
    def _generate_summary(self, analyzed_games: List[Dict[str, Any]]) -> str:
        """Generate a summary report of all analyzed games."""
        if not analyzed_games:
            return "No games analyzed."
        
        summary_lines = []
        summary_lines.append(f"\nTotal Live Games Analyzed: {len(analyzed_games)}")
        summary_lines.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_lines.append("\n" + "─"*80)
        
        # Categorize by sport
        nba_games = [g for g in analyzed_games if g.get('sport') == 'NBA']
        nfl_games = [g for g in analyzed_games if g.get('sport') == 'NFL']
        
        summary_lines.append(f"\n🏀 NBA Games: {len(nba_games)}")
        summary_lines.append(f"🏈 NFL Games: {len(nfl_games)}")
        
        # Categorize recommendations
        bets_recommended = []
        no_bets = []
        errors = []
        
        for game in analyzed_games:
            if "error" in game:
                errors.append(game)
            elif "no bet" in game.get("recommendation", "").lower() or "avoid" in game.get("recommendation", "").lower():
                no_bets.append(game)
            else:
                bets_recommended.append(game)
        
        summary_lines.append(f"\n✅ Games with Betting Opportunities: {len(bets_recommended)}")
        for game in bets_recommended:
            ev = game.get('expected_value', 0)
            ev_str = f"{ev:+.1%}" if ev != 0 else "0.0%"
            sport_emoji = "🏀" if game.get('sport') == 'NBA' else "🏈"
            summary_lines.append(f"  {sport_emoji} {game.get('team1')} vs {game.get('team2')}: {game.get('recommendation')} (EV: {ev_str})")
        
        summary_lines.append(f"\n⚠️  Games to Avoid: {len(no_bets)}")
        for game in no_bets:
            sport_emoji = "🏀" if game.get('sport') == 'NBA' else "🏈"
            summary_lines.append(f"  {sport_emoji} {game.get('team1')} vs {game.get('team2')}: {game.get('recommendation')}")
        
        if errors:
            summary_lines.append(f"\n❌ Games with Errors: {len(errors)}")
            for game in errors:
                summary_lines.append(f"  • {game.get('team1')} vs {game.get('team2')}: {game.get('error')}")
        
        summary_lines.append("\n" + "─"*80)
        summary_lines.append("⚠️  DISCLAIMER: This analysis is for informational purposes only.")
        summary_lines.append("   Always gamble responsibly and within your means.")
        summary_lines.append("   Past performance does not guarantee future results.")
        summary_lines.append("─"*80)
        
        return "\n".join(summary_lines)


def main():
    """Main entry point."""
    try:
        agent = GeminiLiveGamesAgent()
        result = agent.get_comprehensive_analysis()
        
        if result.get("live_games_count", 0) == 0:
            print("\n💡 Tips:")
            print("  • NBA games typically run: Evening hours (7 PM - 11 PM EST)")
            print("  • NFL games typically run: Sunday afternoons/evenings, Monday nights")
            print("  • Try running this script during game hours for best results")
        
        return 0
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

