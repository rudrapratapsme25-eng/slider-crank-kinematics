import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

# ==========================================
# 1. DIMENSIONS & GEAR PARAMETERS
# ==========================================
# Linkage and Piston (from your table)
rod_length = 120.0
piston_dia = 60.0
piston_len = 80.0
piston_pin_offset = 30.0

# Epicyclic (Planetary) Parameters
carrier_radius = 35.0                 # The main crank radius provided
sun_radius = 20.0                     # Assumed stationary center gear radius
planet_radius = carrier_radius - sun_radius # Calculated: 15.0 mm
planet_pin_offset = planet_radius     # Pin located on the edge of the planet gear

# ==========================================
# 2. CALCULATE KINEMATIC COORDINATES
# ==========================================
# Using 720 degrees (4*pi) because planetary setups often take 
# multiple carrier revolutions to complete one full pin cycle
theta = np.linspace(0, 4 * np.pi, 720) 

# Fixed Origin (Sun Gear Center)
Ox, Oy = 0, 0 

# Planet Gear Center (Moves in a circle of radius 35mm)
Px = carrier_radius * np.cos(theta)
Py = carrier_radius * np.sin(theta)

# Joint A: Crank pin on the rotating Planet Gear
# The planet gear rotates relative to the carrier by (Sun/Planet) ratio
planet_angle = theta * (1 + (sun_radius / planet_radius))
Ax = Px + planet_pin_offset * np.cos(planet_angle)
Ay = Py + planet_pin_offset * np.sin(planet_angle)

# Joint B: Wrist pin (Moves linearly along X-axis inside Piston)
# Note: np.maximum prevents NaN errors if the math allows the rod to pull too far
Bx = Ax + np.sqrt(np.maximum(rod_length**2 - Ay**2, 0))
By = np.zeros_like(theta)

# ==========================================
# 3. ANIMATION SETUP
# ==========================================
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_title('Epicyclic Gear Slider-Crank Simulation')
ax.set_xlabel('X Position (mm)')
ax.set_ylabel('Y Position (mm)')

# Set dynamic axis limits
max_reach = carrier_radius + planet_pin_offset + rod_length + (piston_len - piston_pin_offset) + 10
ax.set_xlim(-carrier_radius - planet_pin_offset - 20, max_reach)
ax.set_ylim(-carrier_radius - planet_pin_offset - 20, carrier_radius + planet_pin_offset + 20)

# --- Static Elements ---
sun_gear = patches.Circle((Ox, Oy), sun_radius, fill=False, color='black', lw=2, linestyle='dashed')
ax.add_patch(sun_gear)
ax.axhline(piston_dia/2 + 1, xmin=0.4, color='black', lw=2)
ax.axhline(-piston_dia/2 - 1, xmin=0.4, color='black', lw=2)

# --- Dynamic Elements ---
carrier_line, = ax.plot([], [], 'k--', lw=2, label='Carrier Arm')
planet_gear = patches.Circle((0, 0), planet_radius, fill=False, color='purple', lw=2)
ax.add_patch(planet_gear)

line_rod, = ax.plot([], [], 'o-', lw=4, color='blue', label='Connecting Rod')
pin_trace, = ax.plot([], [], 'r-', lw=1, alpha=0.5, label='Pin Path (Epitrochoid)')
piston_rect = patches.Rectangle((0, 0), piston_len, piston_dia, fill=True, color='orange', alpha=0.6)
ax.add_patch(piston_rect)

ax.legend(loc='upper right')

# ==========================================
# 4. ANIMATION FUNCTIONS
# ==========================================
# Store trace history
trace_x, trace_y = [], []

def init():
    carrier_line.set_data([], [])
    planet_gear.set_center((Px[0], Py[0]))
    line_rod.set_data([], [])
    pin_trace.set_data([], [])
    piston_rect.set_xy((0, 0))
    trace_x.clear()
    trace_y.clear()
    return carrier_line, planet_gear, line_rod, pin_trace, piston_rect

def animate(i):
    # Update Carrier & Planet Gear
    carrier_line.set_data([Ox, Px[i]], [Oy, Py[i]])
    planet_gear.set_center((Px[i], Py[i]))
    
    # Update Linkages
    line_rod.set_data([Ax[i], Bx[i]], [Ay[i], By[i]])
    
    # Update Pin Trace
    trace_x.append(Ax[i])
    trace_y.append(Ay[i])
    pin_trace.set_data(trace_x, trace_y)
    
    # Update Piston
    piston_x = Bx[i] - piston_pin_offset
    piston_y = -piston_dia / 2
    piston_rect.set_xy((piston_x, piston_y))
    
    return carrier_line, planet_gear, line_rod, pin_trace, piston_rect

ani = animation.FuncAnimation(
    fig, animate, init_func=init, 
    frames=len(theta), interval=15, blit=True
)

plt.show()