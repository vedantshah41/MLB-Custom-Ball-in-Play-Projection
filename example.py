"""
Example script demonstrating how to use the MLB Hitter vs Stadium Comparison project
"""

from src.comparison import compare_hitter_to_all_stadiums, get_best_stadium_matches
from src.stadiums import get_stadium_dataframe
from src.hitter_data import get_all_hitters, get_hitter_summary_stats
import pandas as pd


def example_compare_single_hitter():
    """Example: Compare a single hitter to all stadiums"""
    print("Example 1: Comparing a single hitter to all stadiums")
    print("-" * 60)
    
    # First, let's get a list of hitters to choose from
    hitters = get_all_hitters(2024)
    
    if len(hitters) > 0:
        # Get the first hitter as an example
        example_hitter = hitters.iloc[0]
        player_id = example_hitter['IDfg']
        player_name = example_hitter.get('full_name', f"Player {player_id}")
        
        print(f"Analyzing: {player_name}")
        print(f"Team: {example_hitter.get('Team', 'Unknown')}")
        print(f"Plate Appearances: {example_hitter.get('PA', 'Unknown')}")
        
        # Compare to all stadiums
        comparisons = compare_hitter_to_all_stadiums(player_id, player_name, 2024)
        
        if len(comparisons) > 0:
            # Show top 5 matches
            top_matches = get_best_stadium_matches(player_name, comparisons, top_n=5)
            
            print("\nTop 5 Stadium Matches:")
            print(top_matches[['stadium_name', 'team', 'overall_match_score', 
                              'park_factor', 'stadium_advantage']].to_string(index=False))
        else:
            print("No comparison data available for this hitter.")
    else:
        print("No hitters found. Please check your data connection.")


def example_view_stadiums():
    """Example: View all stadium information"""
    print("\nExample 2: Viewing all MLB stadiums")
    print("-" * 60)
    
    stadiums_df = get_stadium_dataframe()
    
    # Display key information
    display_cols = ['stadium_name', 'team', 'city', 'park_factor', 
                   'left_field', 'center_field', 'right_field']
    
    print("\nAll MLB Stadiums:")
    print(stadiums_df[display_cols].to_string(index=False))
    
    # Show stadiums by park factor
    print("\nStadiums ranked by Park Factor (hitter-friendly to pitcher-friendly):")
    ranked = stadiums_df.sort_values('park_factor', ascending=False)
    print(ranked[['stadium_name', 'team', 'park_factor']].to_string(index=False))


def example_hitter_summary():
    """Example: Get summary statistics for a hitter"""
    print("\nExample 3: Getting hitter summary statistics")
    print("-" * 60)
    
    hitters = get_all_hitters(2024)
    
    if len(hitters) > 0:
        example_hitter = hitters.iloc[0]
        player_id = example_hitter['IDfg']
        player_name = example_hitter.get('full_name', f"Player {player_id}")
        
        print(f"Getting stats for: {player_name}")
        
        summary = get_hitter_summary_stats(player_id, 2024)
        
        if summary:
            print("\nHitter Summary Statistics:")
            for key, value in summary.items():
                if value is not None:
                    if isinstance(value, float):
                        print(f"  {key}: {value:.3f}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("No summary statistics available for this hitter.")
    else:
        print("No hitters found.")


if __name__ == '__main__':
    print("=" * 60)
    print("MLB Hitter vs Stadium Comparison - Examples")
    print("=" * 60)
    
    # Run examples
    example_view_stadiums()
    example_hitter_summary()
    example_compare_single_hitter()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nTo run the full analysis, use:")
    print("  python main.py --year 2024 --min-pa 100")
    print("\nFor more options:")
    print("  python main.py --help")
