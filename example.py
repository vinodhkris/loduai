"""Example usage of the betting agent."""

from betting_agent import BettingAgent


def main():
    """Example usage of the betting agent."""
    
    # Initialize the agent
    agent = BettingAgent(model_name="gemini-pro", temperature=0.3)
    
    # Example 1: Basic analysis with minimal data
    print("="*60)
    print("Example 1: Basic Match Analysis")
    print("="*60)
    
    result1 = agent.analyze_match(
        team1="Manchester United",
        team2="Liverpool",
        team1_odds=2.5,
        team2_odds=1.8,
        draw_odds=3.2
    )
    
    print(f"Recommendation: {result1.get('recommendation')}")
    print(f"Analysis: {result1.get('analysis')[:200]}...")
    print()
    
    # Example 2: Detailed analysis with team data
    print("="*60)
    print("Example 2: Detailed Match Analysis")
    print("="*60)
    
    result2 = agent.analyze_match(
        team1="Barcelona",
        team2="Real Madrid",
        team1_odds=2.1,
        team2_odds=1.9,
        draw_odds=3.5,
        team1_recent_form="WWLWW",
        team2_recent_form="WLWWL",
        team1_record="20W-5L-3D",
        team2_record="18W-7L-3D",
        head_to_head="Barcelona: 5 wins, Real Madrid: 3 wins, Draws: 2",
        home_team="Barcelona",
        additional_context="Barcelona has key players returning from injury"
    )
    
    print(f"Recommendation: {result2.get('recommendation')}")
    print(f"Confidence: {result2.get('confidence', 0):.1%}")
    print(f"Expected Value: {result2.get('expected_value', 0):.1%}")
    print()


if __name__ == "__main__":
    main()

