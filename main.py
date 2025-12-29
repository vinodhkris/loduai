"""CLI interface for the betting agent."""

import argparse
import json
from betting_agent import BettingAgent


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LangChain Betting Agent - Analyze game bets based on team strength and odds"
    )
    
    # Required arguments
    parser.add_argument("--team1", type=str, required=True, help="Name of team 1")
    parser.add_argument("--team2", type=str, required=True, help="Name of team 2")
    parser.add_argument("--odds1", type=float, required=True, help="Decimal odds for team 1")
    parser.add_argument("--odds2", type=float, required=True, help="Decimal odds for team 2")
    
    # Optional arguments
    parser.add_argument("--draw", type=float, help="Decimal odds for draw")
    parser.add_argument("--form1", type=str, help="Recent form for team1 (e.g., WWLWD)")
    parser.add_argument("--form2", type=str, help="Recent form for team2 (e.g., WLWWL)")
    parser.add_argument("--record1", type=str, help="Season record for team1 (e.g., 15W-5L-3D)")
    parser.add_argument("--record2", type=str, help="Season record for team2")
    parser.add_argument("--h2h", type=str, help="Head-to-head record")
    parser.add_argument("--home", type=str, help="Home team name")
    parser.add_argument("--context", type=str, help="Additional context about the match")
    parser.add_argument("--output", type=str, choices=["pretty", "json"], default="pretty", help="Output format")
    parser.add_argument("--model", type=str, default="gemini-pro", help="Gemini model name")
    parser.add_argument("--temperature", type=float, default=0.3, help="Model temperature (0-1)")
    
    args = parser.parse_args()
    
    # Initialize agent
    try:
        agent = BettingAgent(model_name=args.model, temperature=args.temperature)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    # Analyze match
    print("Analyzing match...")
    result = agent.analyze_match(
        team1=args.team1,
        team2=args.team2,
        team1_odds=args.odds1,
        team2_odds=args.odds2,
        draw_odds=args.draw,
        team1_recent_form=args.form1,
        team2_recent_form=args.form2,
        team1_record=args.record1,
        team2_record=args.record2,
        head_to_head=args.h2h,
        home_team=args.home,
        additional_context=args.context,
    )
    
    # Output results
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "="*60)
        print("BETTING ANALYSIS RESULTS")
        print("="*60)
        print(f"\nMatch: {result.get('team1')} vs {result.get('team2')}")
        print(f"Odds: {result.get('team1')} @ {result.get('team1_odds')} | {result.get('team2')} @ {result.get('team2_odds')}")
        if result.get('draw_odds'):
            print(f"Draw @ {result.get('draw_odds')}")
        
        print(f"\nRecommendation: {result.get('recommendation', 'N/A')}")
        if result.get('confidence'):
            print(f"Confidence: {result.get('confidence'):.1%}")
        if result.get('expected_value'):
            print(f"Expected Value: {result.get('expected_value'):.1%}")
        
        print(f"\nDetailed Analysis:\n{result.get('analysis', 'N/A')}")
        print("\n" + "="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())

