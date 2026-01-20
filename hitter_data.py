"""
MLB Hitter Data Module
Fetches and processes balls in play data for MLB hitters.
"""

import pandas as pd
import pybaseball as pyb
from tqdm import tqdm
import time


def get_all_hitters(year=2024):
    """
    Get all MLB hitters for a given year.
    
    Args:
        year (int): Year to fetch data for (default: 2024)
        
    Returns:
        pd.DataFrame: DataFrame containing hitter information
    """
    print(f"Fetching hitter data for {year}...")
    
    try:
        # Get batting stats for all players
        batting_stats = pyb.batting_stats(year, qual=0)  # qual=0 means no minimum PA requirement
        
        # Get player info to match names
        player_info = pyb.playerid_reverse_lookup(batting_stats['IDfg'].tolist(), key_type='fangraphs')
        
        # Merge to get player names
        hitters = batting_stats.merge(
            player_info[['key_fangraphs', 'name_first', 'name_last']],
            left_on='IDfg',
            right_on='key_fangraphs',
            how='left'
        )
        
        # Create full name
        hitters['full_name'] = hitters['name_first'] + ' ' + hitters['name_last']
        
        print(f"Found {len(hitters)} hitters")
        return hitters
        
    except Exception as e:
        print(f"Error fetching hitter data: {e}")
        print("Attempting alternative method...")
        return get_hitters_alternative(year)


def get_hitters_alternative(year=2024):
    """
    Alternative method to get hitters if primary method fails.
    
    Args:
        year (int): Year to fetch data for
        
    Returns:
        pd.DataFrame: DataFrame containing hitter information
    """
    try:
        # Try getting team batting stats and extract players
        teams = pyb.team_ids(year)
        all_hitters = []
        
        for team in tqdm(teams['teamIDBR'], desc="Fetching team rosters"):
            try:
                roster = pyb.roster(team, year)
                if roster is not None and len(roster) > 0:
                    # Filter for position players (exclude pitchers)
                    hitters = roster[~roster['Position'].str.contains('P', na=False)]
                    all_hitters.append(hitters)
                time.sleep(0.1)  # Rate limiting
            except:
                continue
        
        if all_hitters:
            return pd.concat(all_hitters, ignore_index=True)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Alternative method also failed: {e}")
        return pd.DataFrame()


def get_hitter_bip_stats(player_id, year=2024, mlbam_id=None):
    """
    Get balls in play statistics for a specific hitter.
    
    Args:
        player_id (int): FanGraphs player ID
        year (int): Year to fetch data for
        mlbam_id (int): Optional MLBAM player ID (if available)
        
    Returns:
        pd.DataFrame: DataFrame containing BIP statistics
    """
    try:
        # Try to get MLBAM ID if not provided
        if mlbam_id is None:
            try:
                player_lookup = pyb.playerid_reverse_lookup([player_id], key_type='fangraphs')
                if len(player_lookup) > 0 and 'key_mlbam' in player_lookup.columns:
                    mlbam_id = player_lookup.iloc[0]['key_mlbam']
            except:
                pass
        
        # Get Statcast data for the player
        # statcast_batter uses MLBAM ID, not FanGraphs ID
        if mlbam_id is not None and pd.notna(mlbam_id):
            statcast_data = pyb.statcast_batter(f'{year}-01-01', f'{year}-12-31', int(mlbam_id))
        else:
            # Fallback: try with FanGraphs ID (may not work)
            statcast_data = pyb.statcast_batter(f'{year}-01-01', f'{year}-12-31', player_id)
        
        if statcast_data is None or len(statcast_data) == 0:
            return pd.DataFrame()
        
        # Filter for balls in play (exclude strikeouts and walks)
        bip = statcast_data[
            (statcast_data['type'] == 'X') &  # Balls in play
            (statcast_data['launch_speed'].notna()) &
            (statcast_data['launch_angle'].notna())
        ].copy()
        
        return bip
        
    except Exception as e:
        # Silently fail - not all players have Statcast data
        return pd.DataFrame()


def get_hitter_summary_stats(player_id, year=2024, mlbam_id=None):
    """
    Get summary statistics for a hitter's balls in play.
    
    Args:
        player_id (int): FanGraphs player ID
        year (int): Year to fetch data for
        mlbam_id (int): Optional MLBAM player ID (if available)
        
    Returns:
        dict: Dictionary containing summary statistics
    """
    bip = get_hitter_bip_stats(player_id, year, mlbam_id)
    
    if len(bip) == 0:
        return None
    
    summary = {
        'player_id': player_id,
        'year': year,
        'total_bip': len(bip),
        'avg_exit_velocity': bip['launch_speed'].mean(),
        'max_exit_velocity': bip['launch_speed'].max(),
        'avg_launch_angle': bip['launch_angle'].mean(),
        'barrel_rate': (bip['barrel'] == 1).sum() / len(bip) if 'barrel' in bip.columns else None,
        'hard_hit_rate': (bip['launch_speed'] >= 95).sum() / len(bip),
        'pull_rate': (bip['bb_type'] == 'pull').sum() / len(bip) if 'bb_type' in bip.columns else None,
        'oppo_rate': (bip['bb_type'] == 'oppo').sum() / len(bip) if 'bb_type' in bip.columns else None,
        'home_run_rate': (bip['events'] == 'home_run').sum() / len(bip) if 'events' in bip.columns else None,
        'avg_distance': bip['hit_distance_sc'].mean() if 'hit_distance_sc' in bip.columns else None,
    }
    
    return summary


def get_all_hitters_bip_summary(year=2024, min_pa=100):
    """
    Get summary statistics for all hitters with minimum plate appearances.
    
    Args:
        year (int): Year to fetch data for
        min_pa (int): Minimum plate appearances required
        
    Returns:
        pd.DataFrame: DataFrame containing summary statistics for all hitters
    """
    hitters = get_all_hitters(year)
    
    if len(hitters) == 0:
        return pd.DataFrame()
    
    # Filter by minimum plate appearances
    hitters = hitters[hitters['PA'] >= min_pa]
    
    print(f"Processing BIP stats for {len(hitters)} hitters...")
    
    summaries = []
    for idx, row in tqdm(hitters.iterrows(), total=len(hitters), desc="Processing hitters"):
        try:
            summary = get_hitter_summary_stats(row['IDfg'], year)
            if summary:
                summary['name'] = row.get('full_name', f"Player {row['IDfg']}")
                summary['team'] = row.get('Team', 'Unknown')
                summaries.append(summary)
            time.sleep(0.1)  # Rate limiting
        except Exception as e:
            print(f"Error processing hitter {row.get('full_name', row['IDfg'])}: {e}")
            continue
    
    return pd.DataFrame(summaries)
