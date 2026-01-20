"""
MLB Stadium Information Module
Contains data about all Major League Baseball stadiums including dimensions,
park factors, and other relevant information.
"""

import pandas as pd

# MLB Stadium data with dimensions and park factors
STADIUM_DATA = {
    'Yankee Stadium': {
        'team': 'NYY',
        'city': 'New York',
        'state': 'NY',
        'left_field': 318,
        'left_center': 399,
        'center_field': 408,
        'right_center': 385,
        'right_field': 314,
        'park_factor': 0.95,  # Slightly pitcher-friendly
        'altitude': 0
    },
    'Fenway Park': {
        'team': 'BOS',
        'city': 'Boston',
        'state': 'MA',
        'left_field': 310,
        'left_center': 379,
        'center_field': 390,
        'right_center': 420,
        'right_field': 302,
        'park_factor': 1.08,  # Hitter-friendly
        'altitude': 0
    },
    'Rogers Centre': {
        'team': 'TOR',
        'city': 'Toronto',
        'state': 'ON',
        'left_field': 328,
        'left_center': 375,
        'center_field': 400,
        'right_center': 375,
        'right_field': 328,
        'park_factor': 1.02,
        'altitude': 0
    },
    'Tropicana Field': {
        'team': 'TB',
        'city': 'St. Petersburg',
        'state': 'FL',
        'left_field': 315,
        'left_center': 370,
        'center_field': 404,
        'right_center': 370,
        'right_field': 322,
        'park_factor': 0.92,  # Very pitcher-friendly
        'altitude': 0
    },
    'Oriole Park at Camden Yards': {
        'team': 'BAL',
        'city': 'Baltimore',
        'state': 'MD',
        'left_field': 333,
        'left_center': 364,
        'center_field': 400,
        'right_center': 373,
        'right_field': 318,
        'park_factor': 1.05,
        'altitude': 0
    },
    'Guaranteed Rate Field': {
        'team': 'CWS',
        'city': 'Chicago',
        'state': 'IL',
        'left_field': 330,
        'left_center': 375,
        'center_field': 400,
        'right_center': 375,
        'right_field': 335,
        'park_factor': 1.03,
        'altitude': 0
    },
    'Progressive Field': {
        'team': 'CLE',
        'city': 'Cleveland',
        'state': 'OH',
        'left_field': 325,
        'left_center': 370,
        'center_field': 400,
        'right_center': 375,
        'right_field': 325,
        'park_factor': 0.98,
        'altitude': 0
    },
    'Comerica Park': {
        'team': 'DET',
        'city': 'Detroit',
        'state': 'MI',
        'left_field': 345,
        'left_center': 370,
        'center_field': 420,
        'right_center': 365,
        'right_field': 330,
        'park_factor': 0.96,
        'altitude': 0
    },
    'Kauffman Stadium': {
        'team': 'KC',
        'city': 'Kansas City',
        'state': 'MO',
        'left_field': 330,
        'left_center': 387,
        'center_field': 410,
        'right_center': 387,
        'right_field': 330,
        'park_factor': 0.97,
        'altitude': 0
    },
    'Target Field': {
        'team': 'MIN',
        'city': 'Minneapolis',
        'state': 'MN',
        'left_field': 339,
        'left_center': 377,
        'center_field': 404,
        'right_center': 367,
        'right_field': 328,
        'park_factor': 0.99,
        'altitude': 0
    },
    'Minute Maid Park': {
        'team': 'HOU',
        'city': 'Houston',
        'state': 'TX',
        'left_field': 315,
        'left_center': 362,
        'center_field': 409,
        'right_center': 373,
        'right_field': 326,
        'park_factor': 1.04,
        'altitude': 0
    },
    'Angel Stadium': {
        'team': 'LAA',
        'city': 'Anaheim',
        'state': 'CA',
        'left_field': 330,
        'left_center': 382,
        'center_field': 400,
        'right_center': 365,
        'right_field': 330,
        'park_factor': 0.98,
        'altitude': 0
    },
    'Oakland Coliseum': {
        'team': 'OAK',
        'city': 'Oakland',
        'state': 'CA',
        'left_field': 330,
        'left_center': 362,
        'center_field': 400,
        'right_center': 362,
        'right_field': 330,
        'park_factor': 0.92,
        'altitude': 0
    },
    'T-Mobile Park': {
        'team': 'SEA',
        'city': 'Seattle',
        'state': 'WA',
        'left_field': 331,
        'left_center': 390,
        'center_field': 401,
        'right_center': 387,
        'right_field': 326,
        'park_factor': 0.90,  # Very pitcher-friendly
        'altitude': 0
    },
    'Rangers Ballpark': {
        'team': 'TEX',
        'city': 'Arlington',
        'state': 'TX',
        'left_field': 332,
        'left_center': 390,
        'center_field': 400,
        'right_center': 377,
        'right_field': 325,
        'park_factor': 1.06,
        'altitude': 0
    },
    'Truist Park': {
        'team': 'ATL',
        'city': 'Atlanta',
        'state': 'GA',
        'left_field': 335,
        'left_center': 380,
        'center_field': 400,
        'right_center': 375,
        'right_field': 325,
        'park_factor': 1.01,
        'altitude': 0
    },
    'loanDepot park': {
        'team': 'MIA',
        'city': 'Miami',
        'state': 'FL',
        'left_field': 340,
        'left_center': 384,
        'center_field': 407,
        'right_center': 392,
        'right_field': 335,
        'park_factor': 0.94,
        'altitude': 0
    },
    'Citi Field': {
        'team': 'NYM',
        'city': 'New York',
        'state': 'NY',
        'left_field': 335,
        'left_center': 378,
        'center_field': 408,
        'right_center': 415,
        'right_field': 330,
        'park_factor': 0.93,
        'altitude': 0
    },
    'Citizens Bank Park': {
        'team': 'PHI',
        'city': 'Philadelphia',
        'state': 'PA',
        'left_field': 329,
        'left_center': 374,
        'center_field': 401,
        'right_center': 369,
        'right_field': 330,
        'park_factor': 1.05,
        'altitude': 0
    },
    'Nationals Park': {
        'team': 'WSH',
        'city': 'Washington',
        'state': 'DC',
        'left_field': 336,
        'left_center': 377,
        'center_field': 402,
        'right_center': 370,
        'right_field': 335,
        'park_factor': 0.99,
        'altitude': 0
    },
    'Wrigley Field': {
        'team': 'CHC',
        'city': 'Chicago',
        'state': 'IL',
        'left_field': 355,
        'left_center': 368,
        'center_field': 400,
        'right_center': 368,
        'right_field': 353,
        'park_factor': 1.02,
        'altitude': 0
    },
    'Great American Ball Park': {
        'team': 'CIN',
        'city': 'Cincinnati',
        'state': 'OH',
        'left_field': 328,
        'left_center': 379,
        'center_field': 404,
        'right_center': 370,
        'right_field': 325,
        'park_factor': 1.10,  # Very hitter-friendly
        'altitude': 0
    },
    'American Family Field': {
        'team': 'MIL',
        'city': 'Milwaukee',
        'state': 'WI',
        'left_field': 344,
        'left_center': 370,
        'center_field': 400,
        'right_center': 374,
        'right_field': 345,
        'park_factor': 1.00,
        'altitude': 0
    },
    'PNC Park': {
        'team': 'PIT',
        'city': 'Pittsburgh',
        'state': 'PA',
        'left_field': 325,
        'left_center': 389,
        'center_field': 399,
        'right_center': 375,
        'right_field': 320,
        'park_factor': 0.96,
        'altitude': 0
    },
    'Busch Stadium': {
        'team': 'STL',
        'city': 'St. Louis',
        'state': 'MO',
        'left_field': 336,
        'left_center': 375,
        'center_field': 400,
        'right_center': 375,
        'right_field': 335,
        'park_factor': 0.98,
        'altitude': 0
    },
    'Chase Field': {
        'team': 'ARI',
        'city': 'Phoenix',
        'state': 'AZ',
        'left_field': 330,
        'left_center': 374,
        'center_field': 407,
        'right_center': 374,
        'right_field': 335,
        'park_factor': 1.05,
        'altitude': 0
    },
    'Coors Field': {
        'team': 'COL',
        'city': 'Denver',
        'state': 'CO',
        'left_field': 347,
        'left_center': 390,
        'center_field': 415,
        'right_center': 375,
        'right_field': 350,
        'park_factor': 1.30,  # Extremely hitter-friendly due to altitude
        'altitude': 5280
    },
    'Dodger Stadium': {
        'team': 'LAD',
        'city': 'Los Angeles',
        'state': 'CA',
        'left_field': 330,
        'left_center': 368,
        'center_field': 395,
        'right_center': 368,
        'right_field': 330,
        'park_factor': 0.97,
        'altitude': 0
    },
    'Petco Park': {
        'team': 'SD',
        'city': 'San Diego',
        'state': 'CA',
        'left_field': 334,
        'left_center': 378,
        'center_field': 396,
        'right_center': 387,
        'right_field': 322,
        'park_factor': 0.88,  # Very pitcher-friendly
        'altitude': 0
    },
    'Oracle Park': {
        'team': 'SF',
        'city': 'San Francisco',
        'state': 'CA',
        'left_field': 339,
        'left_center': 364,
        'center_field': 399,
        'right_center': 421,
        'right_field': 309,
        'park_factor': 0.89,  # Very pitcher-friendly
        'altitude': 0
    }
}


def get_stadium_dataframe():
    """
    Returns a pandas DataFrame with all stadium information.
    
    Returns:
        pd.DataFrame: DataFrame containing stadium data
    """
    return pd.DataFrame.from_dict(STADIUM_DATA, orient='index').reset_index().rename(columns={'index': 'stadium_name'})


def get_stadium_names():
    """
    Returns a list of all stadium names.
    
    Returns:
        list: List of stadium names
    """
    return list(STADIUM_DATA.keys())


def get_stadium_info(stadium_name):
    """
    Get information for a specific stadium.
    
    Args:
        stadium_name (str): Name of the stadium
        
    Returns:
        dict: Stadium information dictionary
    """
    return STADIUM_DATA.get(stadium_name, None)
