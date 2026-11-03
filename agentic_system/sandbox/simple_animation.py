import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create a figure and a set of subplots
fig, ax = plt.subplots()

# Create a circle
circle, = ax.plot([], [], 'o', ms=20, mfc='r')

# Initialize the data
xdata = []
ydata = []

# Animation function
def init():
    ax.set_xlim(0, 4*np.pi)
    ax.set_ylim(-1.5, 1.5)
    return circle,

def update(frame):
    xdata.append(frame)
    ydata.append(np.sin(frame))
    circle.set_data(xdata, ydata)
    return circle,

# Create the animation
line_ani = FuncAnimation(fig, update, frames=np.linspace(0, 4*np.pi, 100), init_func=init, blit=False)

# Show the plot
plt.show()