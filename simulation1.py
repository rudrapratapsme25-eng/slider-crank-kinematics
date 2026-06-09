import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.widgets import Slider

# ==========================================
# 1. FIXED DIMENSIONS & PARAMETERS
# ==========================================
piston_dia = 60.0
piston_len = 80.0
piston_pin_offset = 30.0

carrier_radius = 35.0
sun_radius = 20.0
planet_radius = 15.0
planet_pin_offset = 15.0

# The epicyclic cycle repeats every 3 carrier revolutions (6*pi radians)
max_angle = 6 * np.pi 
theta_graph = np.linspace(0, max_angle, 500)

def get_kinematics(t, rod_len):
    """Calculates coordinates for a given carrier angle 't' and rod length."""
    Px = carrier_radius * np.cos(t)
    Py = carrier_radius * np.sin(t)
    
    # Planet gear rotation relative to the sun
    planet_angle = t * (1 + (sun_radius / planet_radius))
    Ax = Px + planet_pin_offset * np.cos(planet_angle)
    Ay = Py + planet_pin_offset * np.sin(planet_angle)
    
    # Wrist pin (B) horizontal position
    Bx = Ax + np.sqrt(np.maximum(rod_len**2 - Ay**2, 0))
    return Px, Py, Ax, Ay, Bx

# Pre-calculate initial graph data
_, _, _, _, initial_Bx = get_kinematics(theta_graph, 120.0)

# ==========================================
# 2. FIGURE & SUBPLOT LAYOUT
# ==========================================
fig = plt.figure(figsize=(14, 7))
plt.subplots_adjust(bottom=0.25) # Make room for sliders at the bottom

# Left Subplot: Animation
ax_anim = fig.add_subplot(1, 2, 1)
ax_anim.set_aspect('equal')
ax_anim.grid(True, linestyle='--', alpha=0.6)
ax_anim.set_title('Epicyclic Slider-Crank Simulation')
ax_anim.set_xlabel('X Position (mm)')
ax_anim.set_ylabel('Y Position (mm)')
ax_anim.set_xlim(-80, 250)
ax_anim.set_ylim(-80, 80)

# Right Subplot: Displacement Graph
ax_graph = fig.add_subplot(1, 2, 2)
ax_graph.grid(True, linestyle='--', alpha=0.6)
ax_graph.set_title('Piston Displacement vs. Crank Angle')
ax_graph.set_xlabel('Carrier Angle (Radians)')
ax_graph.set_ylabel('Piston Position (mm)')
ax_graph.set_xlim(0, max_angle)
ax_graph.set_ylim(np.min(initial_Bx) - 10, np.max(initial_Bx) + 10)

# ==========================================
# 3. STATIC & DYNAMIC DRAWING ELEMENTS
# ==========================================
# Static Elements
sun_gear = patches.Circle((0, 0), sun_radius, fill=False, color='black', lw=2, linestyle='dashed')
ax_anim.add_patch(sun_gear)
ax_anim.axhline(piston_dia/2 + 1, xmin=0.3, color='black', lw=2)
ax_anim.axhline(-piston_dia/2 - 1, xmin=0.3, color='black', lw=2)

# Dynamic Animation Elements
carrier_line, = ax_anim.plot([], [], 'k--', lw=2, label='Carrier Arm')
planet_gear = patches.Circle((0, 0), planet_radius, fill=False, color='purple', lw=2)
ax_anim.add_patch(planet_gear)
line_rod, = ax_anim.plot([], [], 'o-', lw=4, color='blue', label='Connecting Rod')
pin_trace, = ax_anim.plot([], [], 'r-', lw=1, alpha=0.5)
piston_rect = patches.Rectangle((0, 0), piston_len, piston_dia, fill=True, color='orange', alpha=0.6)
ax_anim.add_patch(piston_rect)

# Dynamic Graph Elements
line_graph, = ax_graph.plot(theta_graph, initial_Bx, 'b-', lw=2)
dot_graph, = ax_graph.plot([], [], 'ro', markersize=8, label='Current Position')
ax_graph.legend()

# ==========================================
# 4. SLIDER UI SETUP
# ==========================================
ax_rod = fig.add_axes([0.25, 0.1, 0.5, 0.03])
ax_speed = fig.add_axes([0.25, 0.05, 0.5, 0.03])

rod_slider = Slider(ax_rod, 'Rod Length', 80.0, 200.0, valinit=120.0, valstep=1.0)
speed_slider = Slider(ax_speed, 'Crank Speed', 0.01, 0.2, valinit=0.05, valstep=0.01)

def update_graph(val):
    """Recalculates the displacement curve when rod length changes."""
    _, _, _, _, new_Bx = get_kinematics(theta_graph, rod_slider.val)
    line_graph.set_ydata(new_Bx)
    # Dynamically scale the Y-axis so the graph never goes out of bounds
    ax_graph.set_ylim(np.min(new_Bx) - 10, np.max(new_Bx) + 10)
    fig.canvas.draw_idle()

# Trigger update_graph function whenever the rod slider is moved
rod_slider.on_changed(update_graph)

# ==========================================
# 5. ANIMATION LOOP
# ==========================================
current_time = 0.0
trace_x, trace_y = [], []

def animate(frame):
    global current_time
    # Advance time based on the speed slider
    current_time += speed_slider.val 
    
    # Get current coordinates
    Px, Py, Ax, Ay, Bx = get_kinematics(current_time, rod_slider.val)
    
    # Update Animation Plot
    carrier_line.set_data([0, Px], [0, Py])
    planet_gear.set_center((Px, Py))
    line_rod.set_data([Ax, Bx], [Ay, 0])
    
    # Update Pin Trace (limit trace length to 300 to avoid memory lag)
    trace_x.append(Ax)
    trace_y.append(Ay)
    if len(trace_x) > 300:
        trace_x.pop(0)
        trace_y.pop(0)
    pin_trace.set_data(trace_x, trace_y)
    
    # Update Piston Block
    piston_rect.set_xy((Bx - piston_pin_offset, -piston_dia / 2))
    
    # Update Graph Dot Position
    t_mod = current_time % max_angle
    dot_graph.set_data([t_mod], [Bx])
    
    return carrier_line, planet_gear, line_rod, pin_trace, piston_rect, dot_graph

# We use a large frame count, but Matplotlib loops it indefinitely by default
ani = animation.FuncAnimation(fig, animate, frames=200, interval=20, blit=True)

plt.show()