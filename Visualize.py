"""Visualize ThreatFields, Paths, Sensor Locations, GridWorlds

saving videos, need to support ffmpeg
conda install -c conda-forge ffmpeg
"""

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from matplotlib import animation


def draw_threat_field(env, threat_field, x_res=100, y_res=100):
    """Draw a 3D threat field and return an axis object which can be used to update plot

    ax = draw_threat_field(env=env, threat_field=threat_field, x_res = 200, y_res = 200)

    x_res and y_res are optional arguments to change the resolution of the plot, default = 100"""
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Make data
    X = np.linspace(0, env.x_size, x_res)
    Y = np.linspace(0, env.y_size, y_res)
    X, Y = np.meshgrid(X, Y)

    Z = threat_field.threat_value(X, Y)

    # Plot the surface
    surf = ax.plot_surface(X, Y, Z, cmap=cm.jet, linewidth=0, antialiased=False)

    # Customize the z axis
    # ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show(block=False)
    return ax


def animate_threat_field(env, threat_field, x_res=100, y_res=100):
    """Animate a 3D dynamic threat field"""

    def animate(i, Z, surf):
        # Threat field at ith time instant
        Z = threat_field.threat_value(X, Y, T[i])
        ax.clear()
        surf = ax.plot_surface(X, Y, Z, cmap=cm.jet, linewidth=0, antialiased=False)
        # ax.zlim([0, 20])
        return surf,

    # Set up figure, axis, and plot element we want to animate
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Make data
    X = np.linspace(0, env.x_size, x_res)
    Y = np.linspace(0, env.y_size, y_res)
    X, Y = np.meshgrid(X, Y)
    T = np.linspace(0, env.t_final, env.t_pts)
    frames = env.t_pts

    Z = threat_field.threat_value(X, Y, 0)
    surf = ax.plot_surface(X, Y, Z, cmap=cm.jet, linewidth=0, antialiased=False)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    fig.colorbar(surf, shrink=0.5, aspect=5)
    ax.set_xlabel('X nodes - Axis')
    ax.set_ylabel('Y nodes - Axis')
    ax.set_zlabel('Value')

    anim = animation.FuncAnimation(fig, animate, fargs=(Z, surf), frames=frames, interval=20, blit=False, repeat=False)

    plt.show()
    return anim


def animate_test():
    def data(i, z, line):
        z = np.sin(x + y + i)
        ax.clear()
        line = ax.plot_surface(x, y, z, color='b')
        return line,

    n = 2. * np.pi
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = np.linspace(0, n, 100)
    y = np.linspace(0, n, 100)
    x, y = np.meshgrid(x, y)
    z = np.sin(x + y)
    line = ax.plot_surface(x, y, z, color='b')

    ani = animation.FuncAnimation(fig, data, fargs=(z, line), interval=30, blit=False)

    plt.show()


def draw_threat_field_2D(env, threat_field, x_res=100, y_res=100):
    """Draw a 2D threat field and return an axis object to further modify plot

    ax_2d = draw_threat_field_2D(env=env, threat_field=threat_field)

    This function is useful for later plotting the path on top"""
    fig, ax = plt.subplots(1, 1)

    # Make data
    X = np.linspace(0, env.x_size, x_res)
    Y = np.linspace(0, env.y_size, y_res)
    X, Y = np.meshgrid(X, Y)

    Z = threat_field.threat_value(X, Y)

    pcol = ax.pcolor(X, Y, Z, cmap=cm.jet)
    plt.colorbar(pcol)
    plt.show(block=False)
    return ax

def animate_threat_field_2D(env, threat_field, path=None, x_res=100, y_res=100):
    """Animate the time varying threat field in 2D with opttion to plot path"""
    def animate(i, Z, pcol):
        # Threat field at ith time instant
        Z = threat_field.threat_value(X, Y, T[i])
        ax.clear()
        pcol = ax.pcolor(X, Y, Z, cmap=cm.jet)
        # animate_path(ax=ax, path=path, t_idx=i)
        curr_node = path[i]
        ax.plot(curr_node.pos_x, curr_node.pos_y, markersize=10, color='white',
                marker='o', markeredgewidth=2.0, markeredgecolor='black')
        return pcol,

    # Set up figure, axis, and plot element we want to animate
    fig, ax = plt.subplots(1, 1)
    # Make data
    X = np.linspace(0, env.x_size, x_res)
    Y = np.linspace(0, env.y_size, y_res)
    X, Y = np.meshgrid(X, Y)
    T = np.linspace(0, env.t_final, env.t_pts)
    if path:
        frames = len(path)
    else:
        frames = env.t_pts

    Z = threat_field.threat_value(X, Y, 0)
    pcol = ax.pcolor(X, Y, Z, cmap=cm.jet)
    plt.colorbar(pcol)

    anim = animation.FuncAnimation(fig, animate, fargs=(Z, pcol), frames=frames, interval=20, blit=False, repeat=False)

    plt.show()
    return anim


def draw_path(ax, path):
    """Add a path to an existing plot. Used in combination with draw_threat_field_2D.
    Typical usage:

    ax_2d = draw_threat_field_2D(env=env, threat_field=threat_field)
    draw_path(ax=ax_2d, path=path)

    path is a list of Nodes obtained after:

    goal_vertex_found = Astar(graph=graph, start_vertex=start_vertex, goal_vertex=goal_vertex)
    path = [goal_vertex_found.node]
    reconstruct_path(goal_vertex_found, path)"""
    x = [n.pos_x for n in path]
    y = [n.pos_y for n in path]

    ax.plot(x, y, markersize=8, color='white',
            marker='o', markeredgewidth=2.0, markeredgecolor='black')

    plt.show(block=False)


def animate_path(ax, path, t_idx):
    x = [n.pos_x for n in path]
    y = [n.pos_y for n in path]

    ax.plot(x, y, markersize=5, color='white',
            marker='o', markeredgewidth=2.0, markeredgecolor='black')

    # Place current position marker along path
    curr_node = path[t_idx]
    ax.plot(curr_node.pos_x, curr_node.pos_y, markersize=10, color='white',
            marker='o', markeredgewidth=2.0, markeredgecolor='black')

    plt.show(block=False)
