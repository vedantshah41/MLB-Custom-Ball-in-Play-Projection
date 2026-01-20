"""
Visualization Module
Creates heatmaps and visualizations for MLB hitter vs stadium analysis.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns


def create_field_plot():
    """
    Create a baseball field diagram.
    
    Returns:
        fig, ax: matplotlib figure and axes
    """
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 450)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Home plate
    plate = patches.Polygon([(-8.5, 0), (8.5, 0), (0, 17)], 
                           facecolor='white', edgecolor='black', linewidth=2)
    ax.add_patch(plate)
    
    # Infield diamond
    infield = patches.Polygon([(0, 0), (63.64, 63.64), (0, 127.28), (-63.64, 63.64)],
                             facecolor='#90EE90', edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(infield)
    
    # Outfield arc (approximate)
    outfield_arc = patches.Arc((0, 0), 400, 400, angle=0, theta1=45, theta2=135,
                               edgecolor='black', linewidth=2, linestyle='--')
    ax.add_patch(outfield_arc)
    
    # Foul lines
    ax.plot([0, 0], [0, 400], 'k-', linewidth=2)
    ax.plot([-250, 250], [0, 0], 'k-', linewidth=2)
    
    # Base paths
    ax.plot([0, 63.64], [0, 63.64], 'k-', linewidth=1, linestyle='--')
    ax.plot([0, -63.64], [0, 63.64], 'k-', linewidth=1, linestyle='--')
    
    # Bases
    bases = [
        (0, 0, 'HP'),  # Home plate
        (63.64, 63.64, '1B'),
        (0, 127.28, '2B'),
        (-63.64, 63.64, '3B')
    ]
    
    for x, y, label in bases:
        if label == 'HP':
            continue  # Already drawn
        base = patches.Circle((x, y), 7, facecolor='white', edgecolor='black', linewidth=2)
        ax.add_patch(base)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold')
    
    return fig, ax


def plot_bip_heatmap(bip_data, stadium_info=None, player_name="Player"):
    """
    Create a heatmap of balls in play colored by xBA.
    
    Args:
        bip_data (pd.DataFrame): DataFrame with balls in play data including xBA
        stadium_info (dict): Optional stadium information to overlay dimensions
        player_name (str): Player name for title
        
    Returns:
        fig, ax: matplotlib figure and axes
    """
    if len(bip_data) == 0:
        print("No balls in play data to visualize")
        return None, None
    
    # Check if xBA column exists
    if 'estimated_ba_using_speedangle' in bip_data.columns:
        xba_col = 'estimated_ba_using_speedangle'
    elif 'xba' in bip_data.columns:
        xba_col = 'xba'
    elif 'estimated_ba' in bip_data.columns:
        xba_col = 'estimated_ba'
    else:
        # Calculate approximate xBA from exit velocity and launch angle if not available
        print("xBA column not found, calculating from exit velocity and launch angle...")
        bip_data = bip_data.copy()
        bip_data['estimated_xba'] = calculate_xba_from_ev_la(
            bip_data['launch_speed'], 
            bip_data['launch_angle']
        )
        xba_col = 'estimated_xba'
    
    # Get coordinates
    # Statcast uses hc_x and hc_y for hit coordinates
    # These are in pixels on a standardized 250x250 field
    # hc_x: 0-250 pixels (0 = left field line, 125 = center, 250 = right field line)
    # hc_y: 0-250 pixels (0 = home plate, 250 = far outfield)
    # Conversion: x = (hc_x - 125) * 2.5, y = hc_y * 2.5
    if 'hc_x' in bip_data.columns and 'hc_y' in bip_data.columns:
        # Convert Statcast pixel coordinates to feet
        hc_x_pixels = bip_data['hc_x'].values
        hc_y_pixels = bip_data['hc_y'].values
        
        # Filter out invalid coordinates (0,0 or NaN or out of range)
        valid_mask = (hc_x_pixels > 0) & (hc_y_pixels > 0) & \
                     (hc_x_pixels <= 250) & (hc_y_pixels <= 250) & \
                     (~np.isnan(hc_x_pixels)) & (~np.isnan(hc_y_pixels))
        
        if valid_mask.sum() == 0:
            # If no valid hc_x/hc_y, try using hit_distance_sc and spray angle
            print("No valid hc_x/hc_y coordinates, estimating from hit distance and spray angle...")
            if 'hit_distance_sc' in bip_data.columns and 'spray_angle' in bip_data.columns:
                hit_distances = bip_data['hit_distance_sc'].fillna(200).values
                spray_angles = bip_data['spray_angle'].fillna(0).values
                # spray_angle: negative = left field, positive = right field
                x_coords = hit_distances * np.sin(np.radians(spray_angles))
                y_coords = hit_distances * np.cos(np.radians(spray_angles))
            elif 'hit_distance_sc' in bip_data.columns:
                hit_distances = bip_data['hit_distance_sc'].fillna(200).values
                # Estimate direction from bb_type if available
                directions = np.zeros(len(bip_data))
                if 'bb_type' in bip_data.columns:
                    pull_mask = bip_data['bb_type'] == 'pull'
                    oppo_mask = bip_data['bb_type'] == 'oppo'
                    directions[pull_mask] = 30  # Pull side (right for righty, left for lefty)
                    directions[oppo_mask] = -30   # Opposite field
                x_coords = hit_distances * np.sin(np.radians(directions))
                y_coords = hit_distances * np.cos(np.radians(directions))
            else:
                x_coords, y_coords = estimate_hit_location(
                    bip_data['launch_angle'].values,
                    bip_data.get('launch_direction', None),
                    bip_data.get('hit_distance_sc', None)
                )
            xba_values = bip_data[xba_col].fillna(0.3).values
        else:
            # Convert pixels to feet
            # x: negative = left field, positive = right field (in feet)
            # y: distance from home plate (in feet)
            x_coords = (hc_x_pixels[valid_mask] - 125) * 2.5
            y_coords = hc_y_pixels[valid_mask] * 2.5
            
            # Additional filtering for reasonable field positions
            valid_mask2 = (y_coords > 0) & (y_coords < 450) & (np.abs(x_coords) < 350)
            x_coords = x_coords[valid_mask2]
            y_coords = y_coords[valid_mask2]
            
            # Update bip_data to match filtered coordinates
            temp_bip = bip_data[valid_mask].reset_index(drop=True)
            if len(temp_bip) > 0 and len(valid_mask2) > 0:
                bip_data = temp_bip.iloc[valid_mask2].reset_index(drop=True)
            else:
                bip_data = temp_bip
            xba_values = bip_data[xba_col].fillna(0.3).values if len(bip_data) > 0 else np.array([])
    elif 'hit_location_x' in bip_data.columns and 'hit_location_y' in bip_data.columns:
        x_coords = bip_data['hit_location_x'].values
        y_coords = bip_data['hit_location_y'].values
        xba_values = bip_data[xba_col].fillna(0.3).values
    else:
        # Use launch angle and direction to estimate location
        print("Hit coordinates not found, estimating from launch angle and direction...")
        x_coords, y_coords = estimate_hit_location(
            bip_data['launch_angle'].values,
            bip_data.get('launch_direction', None),
            bip_data.get('hit_distance_sc', None)
        )
        xba_values = bip_data[xba_col].fillna(0.3).values
    
    # Check if we have valid data
    if len(x_coords) == 0:
        print("No valid hit coordinates found.")
        return None, None
    
    # Create field plot
    fig, ax = create_field_plot()
    
    # Create color map (green = high xBA, red = low xBA)
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('xba_colormap', colors, N=n_bins)
    
    # Normalize xBA values for coloring
    xba_min, xba_max = xba_values.min(), xba_values.max()
    if xba_max == xba_min:
        xba_max = xba_min + 0.1
    
    normalized_xba = (xba_values - xba_min) / (xba_max - xba_min)
    
    # Plot each ball in play
    scatter = ax.scatter(x_coords, y_coords, c=xba_values, cmap=cmap, 
                        s=50, alpha=0.6, edgecolors='black', linewidths=0.5,
                        vmin=xba_min, vmax=xba_max)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, label='Expected Batting Average (xBA)', 
                       orientation='horizontal', pad=0.05, aspect=40)
    cbar.set_label('Expected Batting Average (xBA)', fontsize=12, fontweight='bold')
    
    # Add stadium dimensions if provided
    if stadium_info:
        draw_stadium_fence(ax, stadium_info)
    
    # Add title with stadium name if available
    if stadium_info:
        stadium_name = stadium_info.get('stadium_name', 'Stadium')
        title = f'{player_name} - Balls in Play at {stadium_name} (Colored by xBA)'
    else:
        title = f'{player_name} - Balls in Play Heatmap (Colored by xBA)'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Add statistics text box
    avg_xba = xba_values.mean()
    total_bip = len(bip_data)
    stats_text = f'Total BIP: {total_bip}\nAvg xBA: {avg_xba:.3f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig, ax


def draw_stadium_fence(ax, stadium_info):
    """
    Draw the actual stadium fence based on stadium dimensions.
    
    Args:
        ax: matplotlib axes
        stadium_info (dict): Stadium information with dimensions
    """
    # Get all fence dimensions
    left_field = stadium_info.get('left_field', 330)
    left_center = stadium_info.get('left_center', 370)
    center_field = stadium_info.get('center_field', 400)
    right_center = stadium_info.get('right_center', 370)
    right_field = stadium_info.get('right_field', 330)
    stadium_name = stadium_info.get('stadium_name', 'Stadium')
    
    # Calculate angles for each fence point
    # Left field line is typically around -45 degrees from center
    # Right field line is typically around +45 degrees from center
    # We'll use these standard angles and adjust distances
    
    # Create fence points with approximate angles
    # Left field: -45 degrees
    # Left-center: -22.5 degrees  
    # Center: 0 degrees
    # Right-center: +22.5 degrees
    # Right field: +45 degrees
    
    angles = np.array([-45, -22.5, 0, 22.5, 45])
    distances = np.array([left_field, left_center, center_field, right_center, right_field])
    
    # Convert to x, y coordinates
    # x: negative = left field, positive = right field
    # y: distance from home plate
    fence_x = distances * np.sin(np.radians(angles))
    fence_y = distances * np.cos(np.radians(angles))
    
    # Create a smooth curve through the points using interpolation
    # Use more points for smoother curve
    fine_angles = np.linspace(-45, 45, 100)
    
    # Interpolate distances for smooth curve
    from scipy.interpolate import interp1d
    try:
        # Use cubic interpolation for smooth curve
        interp_func = interp1d(angles, distances, kind='cubic', fill_value='extrapolate')
        fine_distances = interp_func(fine_angles)
        
        # Convert to x, y coordinates
        fine_fence_x = fine_distances * np.sin(np.radians(fine_angles))
        fine_fence_y = fine_distances * np.cos(np.radians(fine_angles))
        
        # Draw the smooth fence line
        ax.plot(fine_fence_x, fine_fence_y, 'b-', linewidth=4, linestyle='-', 
               alpha=0.8, label=f'{stadium_name} Fence', zorder=10)
    except:
        # Fallback to linear interpolation if scipy not available
        fine_fence_x = []
        fine_fence_y = []
        for angle in fine_angles:
            # Find which segment this angle falls into
            if angle <= -22.5:
                # Between left field and left-center
                t = (angle + 45) / 22.5
                dist = left_field + (left_center - left_field) * t
            elif angle <= 0:
                # Between left-center and center
                t = (angle + 22.5) / 22.5
                dist = left_center + (center_field - left_center) * t
            elif angle <= 22.5:
                # Between center and right-center
                t = angle / 22.5
                dist = center_field + (right_center - center_field) * t
            else:
                # Between right-center and right field
                t = (angle - 22.5) / 22.5
                dist = right_center + (right_field - right_center) * t
            
            fine_fence_x.append(dist * np.sin(np.radians(angle)))
            fine_fence_y.append(dist * np.cos(np.radians(angle)))
        
        ax.plot(fine_fence_x, fine_fence_y, 'b-', linewidth=4, linestyle='-', 
               alpha=0.8, label=f'{stadium_name} Fence', zorder=10)
    
    # Add dimension labels at key points
    label_points = [
        (-45, left_field, 'LF'),
        (-22.5, left_center, 'LC'),
        (0, center_field, 'CF'),
        (22.5, right_center, 'RC'),
        (45, right_field, 'RF')
    ]
    
    for angle, dist, label in label_points:
        x = dist * np.sin(np.radians(angle))
        y = dist * np.cos(np.radians(angle))
        ax.plot([x], [y], 'bo', markersize=8, zorder=11)
        ax.text(x, y + 15, f'{label}\n{dist}ft', ha='center', va='bottom', 
               fontsize=8, fontweight='bold', 
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    ax.legend(loc='upper right', fontsize=10)


def calculate_xba_from_ev_la(exit_velocity, launch_angle):
    """
    Calculate approximate xBA from exit velocity and launch angle.
    This is a simplified model.
    
    Args:
        exit_velocity (array): Exit velocity values
        launch_angle (array): Launch angle values
        
    Returns:
        array: Estimated xBA values
    """
    ev = np.array(exit_velocity)
    la = np.array(launch_angle)
    
    # Simple model: optimal launch angle is around 8-12 degrees
    # Higher exit velocity increases xBA
    # Launch angle sweet spot is 8-12 degrees
    
    # Base xBA from exit velocity
    ev_factor = np.clip((ev - 70) / 30, 0, 1)  # Normalize EV to 0-1
    
    # Launch angle factor (sweet spot around 10 degrees)
    la_factor = 1 - np.abs(la - 10) / 30  # Penalty for being away from 10 degrees
    la_factor = np.clip(la_factor, 0, 1)
    
    # Combine factors
    xba = 0.1 + 0.4 * ev_factor * la_factor
    
    return xba


def estimate_hit_location(launch_angle, launch_direction=None, hit_distance=None):
    """
    Estimate hit location coordinates from launch angle and direction.
    
    Args:
        launch_angle (array): Launch angle values
        launch_direction (array): Optional launch direction (degrees from center)
        hit_distance (array): Optional hit distance
        
    Returns:
        tuple: (x_coords, y_coords) arrays
    """
    la = np.array(launch_angle)
    
    # If no direction provided, assume random distribution
    if launch_direction is None:
        launch_direction = np.random.uniform(-45, 45, len(la))
    else:
        launch_direction = np.array(launch_direction)
    
    # If no distance provided, estimate from launch angle
    if hit_distance is None:
        # Rough estimate: higher launch angle = shorter distance (for grounders)
        # Optimal launch angle (8-12 deg) = longer distance
        hit_distance = 200 + (12 - np.abs(la - 10)) * 10
        hit_distance = np.clip(hit_distance, 50, 450)
    else:
        hit_distance = np.array(hit_distance)
    
    # Convert to x, y coordinates
    # x is horizontal (negative = left field, positive = right field)
    # y is distance from home plate
    angle_rad = np.radians(launch_direction)
    x_coords = hit_distance * np.sin(angle_rad)
    y_coords = hit_distance * np.cos(angle_rad)
    
    return x_coords, y_coords


def save_heatmap(fig, filename='bip_heatmap.png'):
    """
    Save the heatmap figure.
    
    Args:
        fig: matplotlib figure
        filename (str): Output filename
    """
    if fig:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Heatmap saved to {filename}")


def calculate_expected_home_runs(bip_data, stadium_info):
    """
    Calculate how many home runs would occur at a specific stadium based on hit distances and locations.
    
    Args:
        bip_data (pd.DataFrame): Balls in play data with coordinates
        stadium_info (dict): Stadium information with dimensions
        
    Returns:
        int: Number of expected home runs
    """
    if len(bip_data) == 0:
        return 0
    
    # Get stadium dimensions
    left_field = stadium_info.get('left_field', 330)
    center_field = stadium_info.get('center_field', 400)
    right_field = stadium_info.get('right_field', 330)
    
    # Get hit distances
    if 'hit_distance_sc' in bip_data.columns:
        hit_distances = bip_data['hit_distance_sc'].fillna(0).values
    else:
        # Estimate from launch angle and exit velocity if available
        if 'launch_angle' in bip_data.columns and 'launch_speed' in bip_data.columns:
            # Rough estimate: optimal launch angle + high exit velocity = longer distance
            la = bip_data['launch_angle'].values
            ev = bip_data['launch_speed'].values
            # Simple model
            hit_distances = np.clip(ev * 2.5 + (12 - np.abs(la - 10)) * 5, 50, 450)
        else:
            return 0
    
    # Get hit locations (x, y coordinates)
    x_coords = None
    y_coords = None
    
    # Try to get coordinates from hc_x/hc_y
    if 'hc_x' in bip_data.columns and 'hc_y' in bip_data.columns:
        hc_x = bip_data['hc_x'].values
        hc_y = bip_data['hc_y'].values
        valid = (hc_x > 0) & (hc_y > 0) & (hc_x <= 250) & (hc_y <= 250)
        if valid.sum() > 0:
            x_coords = (hc_x[valid] - 125) * 2.5
            y_coords = hc_y[valid] * 2.5
            hit_distances = hit_distances[valid]
    
    # If no coordinates, use spray angle if available
    if x_coords is None and 'spray_angle' in bip_data.columns:
        spray_angles = bip_data['spray_angle'].values
        x_coords = hit_distances * np.sin(np.radians(spray_angles))
        y_coords = hit_distances * np.cos(np.radians(spray_angles))
    
    # If still no coordinates, estimate from distance only (assume center field)
    if x_coords is None:
        x_coords = np.zeros(len(hit_distances))
        y_coords = hit_distances
    
    # Calculate angle from home plate (0 = straight center, positive = right, negative = left)
    angles = np.degrees(np.arctan2(x_coords, y_coords))
    
    # Interpolate fence distance based on angle
    # Left field line is around -45 degrees, right field line is around +45 degrees
    # Center field is 0 degrees
    fence_distances = np.zeros_like(angles)
    
    for i, angle in enumerate(angles):
        if angle <= -30:  # Left field
            # Interpolate between left field and center
            t = (angle + 45) / 15  # Normalize -45 to -30
            fence_distances[i] = left_field + (center_field - left_field) * (1 - t)
        elif angle >= 30:  # Right field
            # Interpolate between center and right field
            t = (angle - 30) / 15  # Normalize 30 to 45
            fence_distances[i] = center_field + (right_field - center_field) * t
        else:  # Center field area (-30 to 30 degrees)
            # Interpolate between left/right and center
            if angle < 0:
                t = (angle + 30) / 30
                fence_distances[i] = left_field + (center_field - left_field) * (1 + t)
            else:
                t = (30 - angle) / 30
                fence_distances[i] = right_field + (center_field - right_field) * (1 + t)
    
    # Count home runs: hit distance >= fence distance
    home_runs = (hit_distances >= fence_distances).sum()
    
    return int(home_runs)


def calculate_expected_stats_for_stadium(bip_data, stadium_info):
    """
    Calculate expected statistics adjusted for stadium.
    
    Args:
        bip_data (pd.DataFrame): Balls in play data
        stadium_info (dict): Stadium information
        
    Returns:
        dict: Dictionary with expected statistics
    """
    if len(bip_data) == 0:
        return {}
    
    park_factor = stadium_info.get('park_factor', 1.0)
    
    # Get xBA if available
    if 'estimated_ba_using_speedangle' in bip_data.columns:
        xba_values = bip_data['estimated_ba_using_speedangle'].fillna(0.3)
    elif 'xba' in bip_data.columns:
        xba_values = bip_data['xba'].fillna(0.3)
    else:
        xba_values = calculate_xba_from_ev_la(
            bip_data['launch_speed'], 
            bip_data['launch_angle']
        )
    
    # Get xSLG if available
    if 'estimated_slg_using_speedangle' in bip_data.columns:
        xslg_values = bip_data['estimated_slg_using_speedangle'].fillna(0.4)
    else:
        # Estimate from xBA
        xslg_values = xba_values * 1.5
    
    # Calculate expected home runs based on stadium dimensions
    expected_hr_count = calculate_expected_home_runs(bip_data, stadium_info)
    expected_hr_rate = expected_hr_count / len(bip_data) if len(bip_data) > 0 else 0
    
    # Get actual HR rate if available
    if 'events' in bip_data.columns:
        actual_hr_count = (bip_data['events'] == 'home_run').sum()
        actual_hr_rate = actual_hr_count / len(bip_data)
    else:
        actual_hr_count = 0
        actual_hr_rate = 0
    
    # Calculate expected stats
    expected_stats = {
        'expected_ba': xba_values.mean(),
        'expected_slg': xslg_values.mean(),
        'expected_ops': xba_values.mean() + xslg_values.mean(),
        'expected_hr_count': expected_hr_count,
        'expected_hr_rate': expected_hr_rate,
        'actual_hr_count': actual_hr_count,
        'actual_hr_rate': actual_hr_rate,
        'total_bip': len(bip_data),
        'park_factor': park_factor,
        'park_adjusted_ba': xba_values.mean() * (1 + (park_factor - 1) * 0.1),  # Rough adjustment
        'park_adjusted_slg': xslg_values.mean() * park_factor,
    }
    
    return expected_stats
