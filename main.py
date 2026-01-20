"""
Main script for MLB Hitter vs Stadium Comparison Project
"""

import pandas as pd
import argparse
from src.comparison import (
    compare_all_hitters_to_stadiums,
    get_best_stadium_matches,
    get_stadium_rankings
)
from src.stadiums import get_stadium_dataframe
from src.hitter_data import get_all_hitters


def main():
    parser = argparse.ArgumentParser(description='Compare MLB hitters to all stadiums')
    parser.add_argument('--year', type=int, default=2024, help='Year to analyze (default: 2024)')
    parser.add_argument('--min-pa', type=int, default=100, help='Minimum plate appearances (default: 100)')
    parser.add_argument('--top-n', type=int, default=None, help='Only analyze top N hitters by PA')
    parser.add_argument('--output', type=str, default='comparisons.csv', help='Output CSV file')
    parser.add_argument('--hitter', type=str, default=None, help='Analyze specific hitter by name')
    parser.add_argument('--list-stadiums', action='store_true', help='List all stadiums and exit')
    parser.add_argument('--list-hitters', action='store_true', help='List all hitters and exit')
    
    args = parser.parse_args()
    
    # List stadiums option
    if args.list_stadiums:
        stadiums_df = get_stadium_dataframe()
        print("\nMLB Stadiums:")
        print(stadiums_df[['stadium_name', 'team', 'city', 'park_factor']].to_string(index=False))
        return
    
    # List hitters option
    if args.list_hitters:
        print(f"\nFetching hitters for {args.year}...")
        hitters = get_all_hitters(args.year)
        if len(hitters) > 0:
            hitters_display = hitters[['full_name', 'Team', 'PA', 'HR', 'AVG']].head(50)
            print("\nTop 50 Hitters:")
            print(hitters_display.to_string(index=False))
        else:
            print("No hitters found!")
        return
    
    # Main analysis
    print("=" * 60)
    print("MLB Hitter vs Stadium Comparison Analysis")
    print("=" * 60)
    print(f"Year: {args.year}")
    print(f"Minimum PA: {args.min_pa}")
    if args.top_n:
        print(f"Top N hitters: {args.top_n}")
    print("=" * 60)
    
    # Run comparison
    comparisons_df = compare_all_hitters_to_stadiums(
        year=args.year,
        min_pa=args.min_pa,
        top_n=args.top_n
    )
    
    if len(comparisons_df) == 0:
        print("\nNo comparison data generated. Please check your inputs.")
        return
    
    # Save to CSV
    comparisons_df.to_csv(args.output, index=False)
    print(f"\nResults saved to {args.output}")
    
    # Show summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    print(f"Total comparisons: {len(comparisons_df)}")
    print(f"Unique hitters: {comparisons_df['player_name'].nunique()}")
    print(f"Unique stadiums: {comparisons_df['stadium_name'].nunique()}")
    
    # Show top stadium matches
    print("\n" + "=" * 60)
    print("Top 10 Stadium Rankings (by average match score)")
    print("=" * 60)
    stadium_rankings = get_stadium_rankings(comparisons_df)
    print(stadium_rankings.head(10).to_string(index=False))
    
    # If specific hitter requested, show their matches
    if args.hitter:
        print(f"\n" + "=" * 60)
        print(f"Best Stadium Matches for {args.hitter}")
        print("=" * 60)
        best_matches = get_best_stadium_matches(args.hitter, comparisons_df, top_n=10)
        if len(best_matches) > 0:
            display_cols = ['stadium_name', 'team', 'overall_match_score', 'park_factor', 
                          'exit_velocity_score', 'hard_hit_score', 'stadium_advantage']
            print(best_matches[display_cols].to_string(index=False))
        else:
            print(f"Hitter '{args.hitter}' not found in results.")
    
    # Show top overall matches
    print("\n" + "=" * 60)
    print("Top 10 Hitter-Stadium Matches")
    print("=" * 60)
    top_matches = comparisons_df.nlargest(10, 'overall_match_score')
    display_cols = ['player_name', 'stadium_name', 'team', 'overall_match_score', 'park_factor']
    print(top_matches[display_cols].to_string(index=False))


if __name__ == '__main__':
    main()
