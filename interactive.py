import pandas as pd
import numpy as np
import pybaseball as pyb
import matplotlib.pyplot as plt
from src.hitter_data import get_all_hitters, get_hitter_bip_stats
from src.stadiums import get_stadium_dataframe, STADIUM_DATA

class BaseballPhysics:
    """Simulates 3D trajectory with Drag and Gravity."""
    G = 32.17  
    CD = 0.3     # Drag coefficient
    MASS = 0.3125 
    AREA = 0.0458 

    @staticmethod
    def get_air_density(altitude):
        """Calculates air density (rho) based on elevation."""
        return 0.075 * np.exp(-altitude / 30000)

    @staticmethod
    def get_height_at_distance(v0_mph, launch_angle, target_dist, altitude):
        """Calculates ball height when it reaches the fence distance."""
        rho = BaseballPhysics.get_air_density(altitude)
        v0 = v0_mph * 1.46667
        theta = np.radians(launch_angle)
        vx, vy = v0 * np.cos(theta), v0 * np.sin(theta)
        x, y, dt = 0.0, 3.0, 0.01
        
        while x < target_dist and y > 0:
            v = np.sqrt(vx**2 + vy**2)
            drag = 0.5 * rho * (v**2) * BaseballPhysics.CD * BaseballPhysics.AREA
            # F = ma -> a = F/m (slugs)
            ax = -(drag * (vx / v)) / 0.0097
            ay = -BaseballPhysics.G - (drag * (vy / v)) / 0.0097
            
            vx += ax * dt
            vy += ay * dt
            x += vx * dt
            y += vy * dt
        return y

def calculate_advanced_stats(bip_data, stadium_info):
    """Refined check: Past wall distance AND higher than wall height."""
    expected_hr = 0
    # Map zones: L (Left), C (Center), R (Right)
    dists = {'L': stadium_info['left_field'], 'C': stadium_info['center_field'], 'R': stadium_info['right_field']}
    heights = stadium_info['wall_heights']

    for _, hit in bip_data.iterrows():
        # Get spray angle (0 is dead center, negative is left, positive is right)
        spray_angle = np.degrees(np.arctan2(hit['hc_x'] - 125.42, 198.27 - hit['hc_y']))
        
        zone = 'L' if spray_angle < -15 else 'R' if spray_angle > 15 else 'C'
        wall_d = dists[zone]
        wall_h = heights[zone]
        
        ball_h_at_wall = BaseballPhysics.get_height_at_distance(
            hit['launch_speed'], hit['launch_angle'], wall_d, stadium_info['altitude']
        )
        
        if hit['hit_distance_sc'] >= wall_d and ball_h_at_wall > wall_h:
            expected_hr += 1
            
    return {"expected_hr": expected_hr, "actual_hr": len(bip_data[bip_data['events'] == 'home_run'])}

def main():
    print("\nMLB HITTER VS STADIUM: ADVANCED PHYSICS")
    year = 2024
    hitters = get_all_hitters(year)
    
    query = input("\nEnter Player Name: ").strip()
    matches = hitters[hitters['full_name'].str.contains(query, case=False, na=False)]
    if matches.empty: return
    
    player = matches.iloc[0]
    stadiums_df = get_stadium_dataframe()
    for i, name in enumerate(stadiums_df['stadium_name'], 1):
        print(f"{i}. {name}")
    
    choice = int(input("\nSelect Stadium Number: "))
    stadium_name = stadiums_df.iloc[choice-1]['stadium_name']
    stadium_info = STADIUM_DATA[stadium_name]
    
    bip_data = get_hitter_bip_stats(player['IDfg'], year)
    results = calculate_advanced_stats(bip_data, stadium_info)
    
    print(f"\nResults for {player['full_name']} at {stadium_name}:")
    print(f"Actual HRs: {results['actual_hr']} | Expected HRs: {results['expected_hr']}")

if __name__ == "__main__":
    main()
