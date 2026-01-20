"""
Comparison Module
Compares MLB hitters' balls in play characteristics with stadium dimensions and park factors.
"""

import pandas as pd
import numpy as np
import pybaseball as pyb
from src.stadiums import get_stadium_dataframe, STADIUM_DATA
from src.hitter_data import get_hitter_bip_stats, get_hitter_summary_stats


def calculate_stadium_match_score(hitter_stats, stadium_info):
    """
    Calculate how well a hitter's profile matches a stadium.
    
    Args:
        hitter_stats (dict): Dictionary containing hitter's BIP statistics
        stadium_info (dict): Dictionary containing stadium information
        
    Returns:
        dict: Dictionary containing match scores and analysis
    """
    if hitter_stats is None or stadium_info is None:
        return None
    
    scores = {}
    
    # Exit velocity analysis
    avg_ev = hitter_stats.get('avg_exit_velocity', 0)
    hard_hit_rate = hitter_stats.get('hard_hit_rate', 0)
    park_factor = stadium_info.get('park_factor', 1.0)
    
    # Higher exit velocity benefits more from hitter-friendly parks
    ev_score = avg_ev * park_factor
    
    # Launch angle analysis
    avg_launch_angle = hitter_stats.get('avg_launch_angle', 0)
    
    # Stadium dimensions
    left_field = stadium_info.get('left_field', 330)
    center_field = stadium_info.get('center_field', 400)
    right_field = stadium_info.get('right_field', 330)
    avg_distance = hitter_stats.get('avg_distance', 0)
    
    # Pull/opposite field analysis
    pull_rate = hitter_stats.get('pull_rate', 0.33)
    oppo_rate = hitter_stats.get('oppo_rate', 0.33)
    
    # Calculate expected home runs based on distance and park factors
    if avg_distance:
        # Simple model: if average distance > stadium dimensions, more HRs expected
        min_dimension = min(left_field, center_field, right_field)
        distance_score = max(0, (avg_distance - min_dimension) / 50) * park_factor
    else:
        distance_score = (hard_hit_rate * park_factor) if hard_hit_rate else 0
    
    # Overall match score (weighted combination)
    overall_score = (
        ev_score * 0.3 +
        hard_hit_rate * park_factor * 100 * 0.3 +
        distance_score * 0.2 +
        park_factor * 20 * 0.2
    )
    
    scores = {
        'exit_velocity_score': ev_score,
        'hard_hit_score': hard_hit_rate * park_factor * 100,
        'distance_score': distance_score,
        'park_factor_boost': park_factor,
        'overall_match_score': overall_score,
        'expected_home_runs': hitter_stats.get('home_run_rate', 0) * park_factor * 100 if hitter_stats.get('home_run_rate') else None,
        'stadium_advantage': 'Hitter-friendly' if park_factor > 1.05 else 'Pitcher-friendly' if park_factor < 0.95 else 'Neutral'
    }
    
    return scores


def compare_hitter_to_all_stadiums(player_id, player_name, year=2024, mlbam_id=None):
    """
    Compare a single hitter's profile to all MLB stadiums.
    
    Args:
        player_id (int): FanGraphs player ID
        player_name (str): Player name
        year (int): Year to analyze
        mlbam_id (int): Optional MLBAM player ID
        
    Returns:
        pd.DataFrame: DataFrame with comparison results for all stadiums
    """
    hitter_stats = get_hitter_summary_stats(player_id, year, mlbam_id)
    
    if hitter_stats is None:
        return pd.DataFrame()
    
    comparisons = []
    
    for stadium_name, stadium_info in STADIUM_DATA.items():
        match_scores = calculate_stadium_match_score(hitter_stats, stadium_info)
        
        if match_scores:
            comparison = {
                'player_id': player_id,
                'player_name': player_name,
                'stadium_name': stadium_name,
                'team': stadium_info['team'],
                **match_scores,
                **stadium_info
            }
            comparisons.append(comparison)
    
    return pd.DataFrame(comparisons)


def compare_all_hitters_to_stadiums(year=2024, min_pa=100, top_n=None):
    """
    Compare all MLB hitters to all stadiums.
    
    Args:
        year (int): Year to analyze
        min_pa (int): Minimum plate appearances required
        top_n (int): If specified, only analyze top N hitters by PA
        
    Returns:
        pd.DataFrame: DataFrame with all comparisons
    """
    from src.hitter_data import get_all_hitters
    
    print("Fetching all hitters...")
    hitters = get_all_hitters(year)
    
    if len(hitters) == 0:
        print("No hitters found!")
        return pd.DataFrame()
    
    # Filter by minimum PA
    hitters = hitters[hitters['PA'] >= min_pa]
    
    # Sort by PA and take top N if specified
    hitters = hitters.sort_values('PA', ascending=False)
    if top_n:
        hitters = hitters.head(top_n)
    
    print(f"Comparing {len(hitters)} hitters to all stadiums...")
    
    all_comparisons = []
    
    for idx, row in hitters.iterrows():
        player_id = row['IDfg']
        player_name = row.get('full_name', f"Player {player_id}")
        
        # Try to get MLBAM ID for better Statcast data access
        mlbam_id = None
        try:
            from src.hitter_data import get_all_hitters
            player_lookup = pyb.playerid_reverse_lookup([player_id], key_type='fangraphs')
            if len(player_lookup) > 0 and 'key_mlbam' in player_lookup.columns:
                mlbam_id = player_lookup.iloc[0]['key_mlbam']
        except:
            pass
        
        print(f"Processing {player_name}...")
        
        comparisons = compare_hitter_to_all_stadiums(player_id, player_name, year, mlbam_id)
        
        if len(comparisons) > 0:
            all_comparisons.append(comparisons)
    
    if len(all_comparisons) > 0:
        return pd.concat(all_comparisons, ignore_index=True)
    else:
        return pd.DataFrame()


def get_best_stadium_matches(hitter_name, comparisons_df, top_n=5):
    """
    Get the best stadium matches for a specific hitter.
    
    Args:
        hitter_name (str): Name of the hitter
        comparisons_df (pd.DataFrame): DataFrame with all comparisons
        top_n (int): Number of top matches to return
        
    Returns:
        pd.DataFrame: DataFrame with top stadium matches
    """
    hitter_comparisons = comparisons_df[comparisons_df['player_name'] == hitter_name]
    
    if len(hitter_comparisons) == 0:
        return pd.DataFrame()
    
    return hitter_comparisons.nlargest(top_n, 'overall_match_score')


def get_stadium_rankings(comparisons_df):
    """
    Get overall rankings of stadiums based on average match scores.
    
    Args:
        comparisons_df (pd.DataFrame): DataFrame with all comparisons
        
    Returns:
        pd.DataFrame: DataFrame with stadium rankings
    """
    stadium_stats = comparisons_df.groupby('stadium_name').agg({
        'overall_match_score': ['mean', 'std', 'count'],
        'park_factor': 'first',
        'team': 'first'
    }).reset_index()
    
    stadium_stats.columns = ['stadium_name', 'avg_match_score', 'std_match_score', 'num_hitters', 'park_factor', 'team']
    stadium_stats = stadium_stats.sort_values('avg_match_score', ascending=False)
    
    return stadium_stats
