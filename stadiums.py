"""
MLB Stadium Information Module
Updated 2026: Includes Wall Heights and Altitude for Physics Simulations.
"""

import pandas as pd

# MLB Stadium data with dimensions, wall heights (ft), and altitude (ft)
STADIUM_DATA = {
    'Yankee Stadium': {
        'team': 'NYY',
        'city': 'New York', 'state': 'NY',
        'left_field': 318, 'left_center': 399, 'center_field': 408, 'right_center': 385, 'right_field': 314,
        'wall_heights': {'L': 8, 'C': 8, 'R': 8},
        'park_factor': 0.95, 'altitude': 54
    },
    'Fenway Park': {
        'team': 'BOS',
        'city': 'Boston', 'state': 'MA',
        'left_field': 310, 'left_center': 379, 'center_field': 390, 'right_center': 420, 'right_field': 302,
        'wall_heights': {'L': 37.2, 'C': 10, 'R': 3},  # Green Monster and Pesky Pole area
        'park_factor': 1.08, 'altitude': 20
    },
    'Coors Field': {
        'team': 'COL',
        'city': 'Denver', 'state': 'CO',
        'left_field': 347, 'left_center': 390, 'center_field': 415, 'right_center': 375, 'right_field': 350,
        'wall_heights': {'L': 8, 'C': 8, 'R': 14},
        'park_factor': 1.30, 'altitude': 5280
    },
    'Kauffman Stadium': {
        'team': 'KC',
        'city': 'Kansas City', 'state': 'MO',
        'left_field': 330, 'left_center': 379, 'center_field': 410, 'right_center': 379, 'right_field': 330,
        'wall_heights': {'L': 8.5, 'C': 8.5, 'R': 8.5}, # Updated for 2026 renovations
        'park_factor': 1.02, 'altitude': 880
    },
    'Oracle Park': {
        'team': 'SF',
        'city': 'San Francisco', 'state': 'CA',
        'left_field': 339, 'left_center': 399, 'center_field': 391, 'right_center': 415, 'right_field': 309,
        'wall_heights': {'L': 8, 'C': 8, 'R': 24}, # The high brick wall in Right Field
        'park_factor': 0.89, 'altitude': 63
    },
    'Progressive Field': {
        'team': 'CLE',
        'city': 'Cleveland', 'state': 'OH',
        'left_field': 325, 'left_center': 370, 'center_field': 400, 'right_center': 375, 'right_field': 325,
        'wall_heights': {'L': 19, 'C': 8, 'R': 8}, # High wall in Left Field
        'park_factor': 0.98, 'altitude': 580
    },
    'Minute Maid Park': {
        'team': 'HOU',
        'city': 'Houston', 'state': 'TX',
        'left_field': 315, 'left_center': 362, 'center_field': 409, 'right_center': 373, 'right_field': 326,
        'wall_heights': {'L': 21, 'C': 8, 'R': 7},
        'park_factor': 1.04, 'altitude': 50
    },
    'Great American Ball Park': {
        'team': 'CIN',
        'city': 'Cincinnati', 'state': 'OH',
        'left_field': 328, 'left_center': 379, 'center_field': 404, 'right_center': 370, 'right_field': 325,
        'wall_heights': {'L': 12, 'C': 8, 'R': 8},
        'park_factor': 1.10, 'altitude': 480
    },
    'Rogers Centre': {
        'team': 'TOR',
        'city': 'Toronto', 'state': 'ON',
        'left_field': 328, 'left_center': 375, 'center_field': 400, 'right_center': 375, 'right_field': 328,
        'wall_heights': {'L': 10, 'C': 10, 'R': 10},
        'park_factor': 1.02, 'altitude': 250
    },
    'Petco Park': {
        'team': 'SD',
        'city': 'San Diego', 'state': 'CA',
        'left_field': 334, 'left_center': 378, 'center_field': 396, 'right_center': 387, 'right_field': 322,
        'wall_heights': {'L': 8, 'C': 8, 'R': 8}, # Deep gaps make this pitcher-friendly
        'park_factor': 0.88, 'altitude': 15
    }
}

# --- HELPER FUNCTIONS ---

def get_stadium_dataframe():
    """Returns a pandas DataFrame with all stadium information."""
    return pd.DataFrame.from_dict(STADIUM_DATA, orient='index').reset_index().rename(columns={'index': 'stadium_name'})

def get_stadium_info(stadium_name):
    """Get information for a specific stadium."""
    return STADIUM_DATA.get(stadium_name, None)

def get_fence_params(stadium_name, spray_angle):
    """
    Returns (distance, height) for a specific part of the wall.
    Args:
        stadium_name: str
        spray_angle: float (degrees, -45 to 45)
    """
    s = STADIUM_DATA.get(stadium_name)
    if not s: return 400, 8
    
    # Logic to map spray angle to distance/height keys
    if spray_angle < -15:
        return s['left_field'], s['wall_heights']['L']
    elif spray_angle < 15:
        return s['center_field'], s['wall_heights']['C']
    else:
        return s['right_field'], s['wall_heights']['R']
