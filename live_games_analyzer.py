"""Script to find and analyze all live games with betting recommendations."""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

from betting_agent import BettingAgent


class LiveGamesFetcher:
    """Fetches live games from various sports APIs."""
    
    def __init__(self):
        self.odds_api_key = os.getenv("THE_ODDS_API_KEY")
        self.sports_data_key = os.getenv("SPORTS_DATA_API_KEY")
    
    def fetch_live_games_odds_api(self) -> List[Dict[str, Any]]:
        """Fetch live games from The Odds API."""
        if not self.odds_api_key:
            return []
        
        try:
            # The Odds API endpoint for live odds
            base_url = "https://api.the-odds-api.com/v4/sports/upcoming/odds"
            params = {
                "apiKey": self.odds_api_key,
                "regions": "us,uk",
                "markets": "h2h",
                "oddsFormat": "decimal"
            }
            
            # Build URL with query parameters
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{base_url}?{query_string}"
            
            # Make request using urllib
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            live_games = []
            current_time = datetime.now(timezone.utc)
            
            for game in data:
                # Check if game is live (commence_time is in the past and within last 3 hours)
                commence_time_str = game.get("commence_time")
                if commence_time_str:
                    try:
                        commence_time = datetime.fromisoformat(
                            commence_time_str.replace("Z", "+00:00")
                        )
                        # Consider games live if they started in the last 3 hours
                        time_diff = (current_time - commence_time).total_seconds()
                        if 0 <= time_diff <= 10800:  # 3 hours in seconds
                            # Extract odds
                            bookmakers = game.get("bookmakers", [])
                            if bookmakers:
                                # Get the first bookmaker's odds
                                markets = bookmakers[0].get("markets", [])
                                if markets:
                                    outcomes = markets[0].get("outcomes", [])
                                    if len(outcomes) >= 2:
                                        team1_name = outcomes[0].get("name", "")
                                        team2_name = outcomes[1].get("name", "")
                                        team1_odds = outcomes[0].get("price", 0)
                                        team2_odds = outcomes[1].get("price", 0)
                                        draw_odds = None
                                        
                                        # Check for draw odds (third outcome)
                                        if len(outcomes) == 3:
                                            draw_odds = outcomes[2].get("price")
                                        
                                        live_games.append({
                                            "sport": game.get("sport_key", "unknown"),
                                            "team1": team1_name,
                                            "team2": team2_name,
                                            "team1_odds": team1_odds,
                                            "team2_odds": team2_odds,
                                            "draw_odds": draw_odds,
                                            "commence_time": commence_time_str,
                                            "home_team": None,  # API doesn't always provide this
                                            "source": "the_odds_api"
                                        })
                    except Exception as e:
                        continue
            
            return live_games
            
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("⚠️  The Odds API: Invalid API key")
            elif e.code == 429:
                print("⚠️  The Odds API: Rate limit exceeded")
            else:
                print(f"⚠️  The Odds API error: {e.code} - {e.reason}")
            return []
        except urllib.error.URLError as e:
            print(f"⚠️  The Odds API: Network error - {e.reason}")
            return []
        except Exception as e:
            print(f"⚠️  Error fetching from The Odds API: {e}")
            return []
    
    def fetch_live_games_sportsradar(self) -> List[Dict[str, Any]]:
        """Fetch live games from SportsRadar API (requires API key)."""
        if not self.sports_data_key:
            return []
        
        try:
            # This is a placeholder - SportsRadar requires specific endpoints
            # You would need to implement based on their API documentation
            return []
        except Exception as e:
            print(f"Error fetching from SportsRadar: {e}")
            return []
    
    def fetch_live_games_web_scraping(self) -> List[Dict[str, Any]]:
        """Fallback: Try to get live games from web scraping (limited)."""
        try:
            # Try to get live games from ESPN or similar
            # Note: This is a simplified approach - in production you'd use proper scraping
            # For now, we'll return empty as web scraping requires more complex setup
            return []
        except Exception as e:
            print(f"Error in web scraping: {e}")
            return []
    
    def get_demo_live_games(self) -> List[Dict[str, Any]]:
        """Get demo/mock live games for testing when no API is available."""
        # This provides sample data for demonstration
        # In a real scenario, you'd fetch actual live games
        return [
            {
                "sport": "soccer",
                "team1": "Manchester United",
                "team2": "Liverpool",
                "team1_odds": 2.5,
                "team2_odds": 1.8,
                "draw_odds": 3.2,
                "commence_time": datetime.now(timezone.utc).isoformat(),
                "home_team": "Manchester United",
                "source": "demo"
            },
            {
                "sport": "basketball",
                "team1": "Lakers",
                "team2": "Warriors",
                "team1_odds": 2.1,
                "team2_odds": 1.9,
                "draw_odds": None,
                "commence_time": datetime.now(timezone.utc).isoformat(),
                "home_team": "Lakers",
                "source": "demo"
            }
        ]
    
    def get_all_live_games(self, use_demo: bool = False) -> List[Dict[str, Any]]:
        """Get all live games from available sources."""
        all_games = []
        
        # If demo mode is requested, return demo games
        if use_demo:
            return self.get_demo_live_games()
        
        # Try The Odds API first
        games = self.fetch_live_games_odds_api()
        all_games.extend(games)
        
        # Try SportsRadar
        games = self.fetch_live_games_sportsradar()
        all_games.extend(games)
        
        # Try web scraping as fallback
        if not all_games:
            games = self.fetch_live_games_web_scraping()
            all_games.extend(games)
        
        # Remove duplicates based on team names
        seen = set()
        unique_games = []
        for game in all_games:
            key = (game["team1"].lower(), game["team2"].lower())
            if key not in seen:
                seen.add(key)
                unique_games.append(game)
        
        return unique_games


class LiveGamesAnalyzer:
    """Analyzes live games and provides betting recommendations."""
    
    def __init__(self):
        self.agent = BettingAgent()
        self.fetcher = LiveGamesFetcher()
    
    def analyze_live_games(self, use_demo: bool = False) -> List[Dict[str, Any]]:
        """Fetch and analyze all live games."""
        print("Fetching live games...")
        live_games = self.fetcher.get_all_live_games(use_demo=use_demo)
        
        if use_demo:
            print("⚠️  Using DEMO mode - showing sample games for demonstration")
            print("   To analyze real live games, set up API keys in .env file\n")
        
        if not live_games:
            print("\n⚠️  No live games found through API.")
            print("This could be because:")
            print("  1. No games are currently live")
            print("  2. API keys are not configured (check .env file)")
            print("  3. API rate limits or connectivity issues")
            print("\n💡 Tip: Set THE_ODDS_API_KEY in your .env file")
            print("   Get a free API key at: https://the-odds-api.com/")
            return []
        
        print(f"\n✅ Found {len(live_games)} live game(s)\n")
        print("="*80)
        
        analyzed_games = []
        
        for idx, game in enumerate(live_games, 1):
            print(f"\n{'='*80}")
            print(f"GAME {idx}/{len(live_games)}: {game['team1']} vs {game['team2']}")
            print(f"{'='*80}")
            print(f"Sport: {game.get('sport', 'Unknown')}")
            print(f"Odds: {game['team1']} @ {game['team1_odds']} | {game['team2']} @ {game['team2_odds']}")
            if game.get('draw_odds'):
                print(f"Draw @ {game['draw_odds']}")
            print(f"Status: LIVE")
            print(f"\nAnalyzing...")
            
            try:
                # Analyze the game
                result = self.agent.analyze_match(
                    team1=game["team1"],
                    team2=game["team2"],
                    team1_odds=game["team1_odds"],
                    team2_odds=game["team2_odds"],
                    draw_odds=game.get("draw_odds"),
                    home_team=game.get("home_team"),
                )
                
                # Add game info to result
                result["sport"] = game.get("sport", "unknown")
                result["status"] = "LIVE"
                result["commence_time"] = game.get("commence_time")
                
                analyzed_games.append(result)
                
                # Print analysis
                print(f"\n{'─'*80}")
                print("📊 ANALYSIS RESULTS")
                print(f"{'─'*80}")
                print(f"\n🎯 Recommendation: {result.get('recommendation', 'N/A')}")
                
                if result.get('confidence'):
                    confidence = result.get('confidence', 0)
                    print(f"📈 Confidence: {confidence:.1%}")
                
                if result.get('expected_value'):
                    ev = result.get('expected_value', 0)
                    ev_display = f"{ev:+.1%}" if ev != 0 else "0.0%"
                    print(f"💰 Expected Value: {ev_display}")
                
                print(f"\n📝 Detailed Analysis:")
                print(f"{'─'*80}")
                analysis = result.get('analysis', 'No analysis available')
                # Print analysis in chunks for better readability
                for line in analysis.split('\n'):
                    if line.strip():
                        print(f"  {line}")
                
                print(f"\n{'─'*80}")
                
            except Exception as e:
                print(f"❌ Error analyzing game: {e}")
                analyzed_games.append({
                    "team1": game["team1"],
                    "team2": game["team2"],
                    "error": str(e),
                    "status": "LIVE"
                })
        
        return analyzed_games
    
    def generate_summary_report(self, analyzed_games: List[Dict[str, Any]]) -> str:
        """Generate a summary report of all analyzed games."""
        if not analyzed_games:
            return "No games analyzed."
        
        report = []
        report.append("\n" + "="*80)
        report.append("📋 SUMMARY REPORT - LIVE GAMES ANALYSIS")
        report.append("="*80)
        report.append(f"\nTotal Games Analyzed: {len(analyzed_games)}")
        report.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n" + "─"*80)
        
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
        
        report.append(f"\n✅ Games with Betting Opportunities: {len(bets_recommended)}")
        for game in bets_recommended:
            ev = game.get('expected_value', 0)
            ev_str = f"{ev:+.1%}" if ev != 0 else "0.0%"
            report.append(f"  • {game.get('team1')} vs {game.get('team2')}: {game.get('recommendation')} (EV: {ev_str})")
        
        report.append(f"\n⚠️  Games to Avoid: {len(no_bets)}")
        for game in no_bets:
            report.append(f"  • {game.get('team1')} vs {game.get('team2')}: {game.get('recommendation')}")
        
        if errors:
            report.append(f"\n❌ Games with Errors: {len(errors)}")
            for game in errors:
                report.append(f"  • {game.get('team1')} vs {game.get('team2')}: {game.get('error')}")
        
        report.append("\n" + "="*80)
        report.append("⚠️  DISCLAIMER: This analysis is for informational purposes only.")
        report.append("   Always gamble responsibly and within your means.")
        report.append("="*80)
        
        return "\n".join(report)


def main():
    """Main entry point."""
    import sys
    
    # Check for demo flag
    use_demo = "--demo" in sys.argv or "-d" in sys.argv
    
    print("\n" + "="*80)
    print("🏈 LIVE GAMES ANALYZER - Betting Recommendations")
    print("="*80)
    
    analyzer = LiveGamesAnalyzer()
    
    # Analyze all live games
    analyzed_games = analyzer.analyze_live_games(use_demo=use_demo)
    
    # Generate and print summary
    if analyzed_games:
        summary = analyzer.generate_summary_report(analyzed_games)
        print(summary)
        
        # Optionally save to file
        output_file = f"live_games_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(analyzed_games, f, indent=2, default=str)
        print(f"\n💾 Full analysis saved to: {output_file}")
    else:
        print("\n" + "="*80)
        print("No live games to analyze at this time.")
        print("="*80)
        print("\n💡 To use this feature:")
        print("   1. Get a free API key from https://the-odds-api.com/")
        print("   2. Add THE_ODDS_API_KEY=your_key_here to your .env file")
        print("   3. Run this script again when games are live")
        print("="*80)


if __name__ == "__main__":
    main()

