import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import interp1d

class TrajectorySim:
    """Simulates 3D flight to check wall clearance."""
    @staticmethod
    def calculate_height_at_fence(v0_mph, launch_angle, target_dist, altitude):
        # Air density adjustment for altitude
        rho = 0.075 * np.exp(-altitude / 30000)
        v0 = v0_mph * 1.46667
        theta = np.radians(launch_angle)
        vx, vy = v0 * np.cos(theta), v0 * np.sin(theta)
        x, y, dt = 0.0, 3.0, 0.01 
        
        while x < target_dist and y > 0:
            v = np.sqrt(vx**2 + vy**2)
            # Drag calculation (Cd=0.3, Area=0.0458, Mass=0.0097)
            f_drag = 0.5 * rho * v**2 * 0.3 * 0.0458
            ax = -(f_drag * (vx / v)) / 0.0097
            ay = -32.17 - (f_drag * (vy / v)) / 0.0097
            vx += ax * dt
            vy += ay * dt
            x += vx * dt
            y += vy * dt
        return y

def create_field_plot():
    """Creates a standardized field diagram."""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 480)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Infield Diamond
    infield = patches.Polygon([(0, 0), (63.6, 63.6), (0, 127.2), (-63.6, 63.6)],
                               facecolor='#90EE90', edgecolor='black', alpha=0.3)
    ax.add_patch(infield)
    
    # Foul Lines (Standard 45-degree lines)
    ax.plot([0, -315], [0, 315], 'k-', linewidth=1.5)
    ax.plot([0, 315], [0, 315], 'k-', linewidth=1.5)
    
    return fig, ax

def plot_bip_heatmap(bip_data, stadium_info, player_name="Player"):
    """Main visualization logic with foul-ball and wall-height correction."""
    if bip_data.empty:
        return None, None

    fig, ax = create_field_plot()
    
    # 1. Correct Spray Angle (Applying the 0.75 correction factor)
    bip_data['spray_angle'] = np.degrees(
        np.arctan((bip_data['hc_x'] - 125.42) / (198.27 - bip_data['hc_y']))
    ) * 0.75
    
    # Use hit_distance_sc for Y, calculate X based on adjusted spray angle
    dist = bip_data['hit_distance_sc'].fillna(0)
    angle_rad = np.radians(bip_data['spray_angle'])
    x_coords = dist * np.sin(angle_rad)
    y_coords = dist * np.cos(angle_rad)

    # 2. 3D Wall Analysis
    expected_hr = 0
    alt = stadium_info.get('altitude', 0)
    
    def get_zone_specs(angle):
        if angle < -15: return stadium_info['left_field'], stadium_info['wall_heights']['L']
        if angle < 15:  return stadium_info['center_field'], stadium_info['wall_heights']['C']
        return stadium_info['right_field'], stadium_info['wall_heights']['R']

    for i, row in bip_data.iterrows():
        w_dist, w_height = get_zone_specs(row['spray_angle'])
        ball_h = TrajectorySim.calculate_height_at_fence(row['launch_speed'], row['launch_angle'], w_dist, alt)
        
        # Must be past distance AND clear the height
        if (row['hit_distance_sc'] >= w_dist) and (ball_h > w_height):
            expected_hr += 1

    # 3. Render Heatmap
    cmap = LinearSegmentedColormap.from_list('xba', ['red', 'orange', 'yellow', 'green'])
    scatter = ax.scatter(x_coords, y_coords, c=bip_data['estimated_ba_using_speedangle'], 
                        cmap=cmap, s=40, alpha=0.7, edgecolors='none', vmin=0, vmax=0.8)
    
    draw_stadium_fence(ax, stadium_info)
    
    plt.colorbar(scatter, ax=ax, label='xBA', orientation='horizontal', pad=0.05)
    ax.set_title(f"{player_name} at {stadium_info['stadium_name']}\nProjected HRs: {expected_hr}", fontsize=14)
    
    return fig, ax

def draw_stadium_fence(ax, stadium_info):
    """Draws a smooth fence line based on stadium dimensions."""
    angles = [-45, -22.5, 0, 22.5, 45]
    dists = [stadium_info['left_field'], stadium_info['left_center'], 
             stadium_info['center_field'], stadium_info['right_center'], stadium_info['right_field']]
    
    f = interp1d(angles, dists, kind='cubic')
    f_angles = np.linspace(-45, 45, 100)
    f_dists = f(f_angles)
    
    fx = f_dists * np.sin(np.radians(f_angles))
    fy = f_dists * np.cos(np.radians(f_angles))
    ax.plot(fx, fy, color='blue', linewidth=3, label="Fence")

    for a, d in zip(angles, dists):
        lx, ly = d * np.sin(np.radians(a)), d * np.cos(np.radians(a))
        ax.text(lx, ly + 10, f"{d}ft", ha='center', fontweight='bold',
                bbox=dict(facecolor='yellow', alpha=0.6, edgecolor='none'))
