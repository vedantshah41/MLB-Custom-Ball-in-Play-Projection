"""
Interactive MLB Hitter vs Stadium Comparison Tool
Asks for player name, shows numbered stadium list, displays expected stats and heatmap.
"""

import pandas as pd
import pybaseball as pyb
import matplotlib.pyplot as plt
from src.hitter_data import get_all_hitters, get_hitter_bip_stats, get_hitter_summary_stats
from src.stadiums import get_stadium_dataframe, STADIUM_DATA
from src.visualization import plot_bip_heatmap, save_heatmap, calculate_expected_stats_for_stadium
from src.comparison import calculate_stadium_match_score


def search_player(query, hitters_df):
    """
    Search for a player by name.
    
    Args:
        query (str): Search query
        hitters_df (pd.DataFrame): DataFrame of all hitters
        
    Returns:
        pd.DataFrame: Matching players
    """
    query_lower = query.lower()
    matches = hitters_df[
        hitters_df['full_name'].str.lower().str.contains(query_lower, na=False)
    ]
    return matches


def display_stadiums():
    """
    Display numbered list of stadiums.
    
    Returns:
        pd.DataFrame: DataFrame with stadium information and numbers
    """
    stadiums_df = get_stadium_dataframe()
    stadiums_df['number'] = range(1, len(stadiums_df) + 1)
    
    print("\n" + "=" * 80)
    print("MLB STADIUMS - Select by number:")
    print("=" * 80)
    
    display_cols = ['number', 'stadium_name', 'team', 'city', 'park_factor']
    for idx, row in stadiums_df.iterrows():
        park_type = "Hitter-friendly" if row['park_factor'] > 1.05 else \
                   "Pitcher-friendly" if row['park_factor'] < 0.95 else "Neutral"
        print(f"{int(row['number']):2d}. {row['stadium_name']:40s} | {row['team']:3s} | "
              f"{row['city']:20s} | PF: {row['park_factor']:.2f} ({park_type})")
    
    print("=" * 80)
    
    return stadiums_df


def get_player_selection(year=2024):
    """
    Interactive player selection.
    
    Args:
        year (int): Year to fetch data for
        
    Returns:
        tuple: (player_id, player_name, mlbam_id) or (None, None, None) if cancelled
    """
    print(f"\nFetching hitters for {year}...")
    hitters = get_all_hitters(year)
    
    if len(hitters) == 0:
        print("Error: Could not fetch hitter data. Please check your internet connection.")
        return None, None, None
    
    print(f"Found {len(hitters)} hitters")
    
    while True:
        print("\nEnter a player name (or 'quit' to exit):")
        query = input("> ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            return None, None, None
        
        if not query:
            print("Please enter a player name.")
            continue
        
        matches = search_player(query, hitters)
        
        if len(matches) == 0:
            print(f"No players found matching '{query}'. Try again.")
            continue
        
        if len(matches) == 1:
            player = matches.iloc[0]
            player_id = player['IDfg']
            player_name = player['full_name']
            print(f"\nSelected: {player_name} ({player.get('Team', 'Unknown')})")
            
            # Get MLBAM ID
            mlbam_id = None
            try:
                player_lookup = pyb.playerid_reverse_lookup([player_id], key_type='fangraphs')
                if len(player_lookup) > 0 and 'key_mlbam' in player_lookup.columns:
                    mlbam_id = player_lookup.iloc[0]['key_mlbam']
            except:
                pass
            
            return player_id, player_name, mlbam_id
        
        # Multiple matches
        print(f"\nFound {len(matches)} players matching '{query}':")
        print("-" * 80)
        for idx, (i, row) in enumerate(matches.iterrows(), 1):
            print(f"{idx}. {row['full_name']} - {row.get('Team', 'Unknown')} "
                  f"(PA: {row.get('PA', 'N/A')}, HR: {row.get('HR', 'N/A')})")
        
        print("\nEnter the number of the player you want (or 'back' to search again):")
        choice = input("> ").strip()
        
        if choice.lower() == 'back':
            continue
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(matches):
                player = matches.iloc[choice_num - 1]
                player_id = player['IDfg']
                player_name = player['full_name']
                print(f"\nSelected: {player_name} ({player.get('Team', 'Unknown')})")
                
                # Get MLBAM ID
                mlbam_id = None
                try:
                    player_lookup = pyb.playerid_reverse_lookup([player_id], key_type='fangraphs')
                    if len(player_lookup) > 0 and 'key_mlbam' in player_lookup.columns:
                        mlbam_id = player_lookup.iloc[0]['key_mlbam']
                except:
                    pass
                
                return player_id, player_name, mlbam_id
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(matches)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_stadium_selection():
    """
    Interactive stadium selection.
    
    Returns:
        tuple: (stadium_name, stadium_info) or (None, None) if cancelled
    """
    stadiums_df = display_stadiums()
    
    while True:
        print("\nEnter the number of the stadium you want to analyze (or 'quit' to exit):")
        choice = input("> ").strip()
        
        if choice.lower() in ['quit', 'exit', 'q']:
            return None, None
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(stadiums_df):
                selected = stadiums_df[stadiums_df['number'] == choice_num].iloc[0]
                stadium_name = selected['stadium_name']
                stadium_info = STADIUM_DATA[stadium_name]
                print(f"\nSelected: {stadium_name} ({stadium_info['team']})")
                return stadium_name, stadium_info
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(stadiums_df)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def display_expected_stats(expected_stats, stadium_name):
    """
    Display expected statistics for the player-stadium combination.
    
    Args:
        expected_stats (dict): Dictionary of expected statistics
        stadium_name (str): Stadium name
    """
    print("\n" + "=" * 80)
    print(f"EXPECTED STATISTICS - {stadium_name}")
    print("=" * 80)
    
    print(f"\nTotal Balls in Play: {expected_stats.get('total_bip', 'N/A')}")
    print(f"Park Factor: {expected_stats.get('park_factor', 'N/A'):.3f}")
    
    print("\nExpected Batting Statistics:")
    print(f"  Expected BA (xBA):     {expected_stats.get('expected_ba', 0):.3f}")
    print(f"  Park-Adjusted BA:      {expected_stats.get('park_adjusted_ba', 0):.3f}")
    print(f"  Expected SLG (xSLG):   {expected_stats.get('expected_slg', 0):.3f}")
    print(f"  Park-Adjusted SLG:     {expected_stats.get('park_adjusted_slg', 0):.3f}")
    print(f"  Expected OPS (xOPS):   {expected_stats.get('expected_ops', 0):.3f}")
    
    print("\nHome Run Analysis:")
    actual_hr = expected_stats.get('actual_hr_count', 0)
    expected_hr = expected_stats.get('expected_hr_count', 0)
    print(f"  Actual Home Runs:      {actual_hr}")
    print(f"  Expected Home Runs:    {expected_hr} (based on stadium dimensions)")
    if actual_hr > 0:
        difference = expected_hr - actual_hr
        print(f"  Difference:            {difference:+d} ({difference/actual_hr*100:+.1f}%)")
    print(f"  Expected HR Rate:      {expected_stats.get('expected_hr_rate', 0):.3%}")
    
    print("\n" + "=" * 80)


def main():
    """
    Main interactive function.
    """
    print("\n" + "=" * 80)
    print("MLB HITTER vs STADIUM COMPARISON TOOL")
    print("=" * 80)
    
    # Ask for year
    while True:
        print("\nEnter the year to analyze (default: 2024, or press Enter to use default):")
        year_input = input("> ").strip()
        
        if not year_input:
            year = 2024
            break
        
        try:
            year = int(year_input)
            if 2015 <= year <= 2024:  # Statcast data available from ~2015
                break
            else:
                print(f"Please enter a year between 2015 and 2024.")
        except ValueError:
            print("Invalid input. Please enter a valid year.")
    
    print(f"\nUsing year: {year}")
    
    # Get player selection
    player_id, player_name, mlbam_id = get_player_selection(year)
    
    if player_id is None:
        print("\nExiting...")
        return
    
    # Get stadium selection
    stadium_name, stadium_info = get_stadium_selection()
    
    if stadium_name is None:
        print("\nExiting...")
        return
    
    # Add stadium name to stadium_info for labeling
    stadium_info['stadium_name'] = stadium_name
    
    # Fetch balls in play data
    print(f"\nFetching balls in play data for {player_name}...")
    bip_data = get_hitter_bip_stats(player_id, year, mlbam_id)
    
    if len(bip_data) == 0:
        print(f"\nError: No balls in play data found for {player_name} in {year}.")
        print("This player may not have Statcast data available.")
        return
    
    print(f"Found {len(bip_data)} balls in play")
    
    # Calculate expected stats
    print("\nCalculating expected statistics...")
    expected_stats = calculate_expected_stats_for_stadium(bip_data, stadium_info)
    
    # Display expected stats
    display_expected_stats(expected_stats, stadium_name)
    
    # Get hitter summary for match score
    hitter_stats = get_hitter_summary_stats(player_id, year, mlbam_id)
    if hitter_stats:
        from src.comparison import calculate_stadium_match_score
        match_scores = calculate_stadium_match_score(hitter_stats, stadium_info)
        
        if match_scores:
            print("\nStadium Match Analysis:")
            print(f"  Overall Match Score:    {match_scores.get('overall_match_score', 0):.2f}")
            print(f"  Exit Velocity Score:    {match_scores.get('exit_velocity_score', 0):.2f}")
            print(f"  Hard Hit Score:        {match_scores.get('hard_hit_score', 0):.2f}")
            print(f"  Stadium Advantage:     {match_scores.get('stadium_advantage', 'N/A')}")
    
    # Create heatmap
    print("\nGenerating heatmap visualization...")
    fig, ax = plot_bip_heatmap(bip_data, stadium_info, player_name)
    
    if fig:
        # Save heatmap
        filename = f"{player_name.replace(' ', '_')}_{stadium_name.replace(' ', '_')}_heatmap.png"
        save_heatmap(fig, filename)
        
        # Show plot
        print("\nDisplaying heatmap... (Close the plot window to continue)")
        plt.show()
    else:
        print("Could not generate heatmap.")
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
