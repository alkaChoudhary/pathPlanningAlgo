"""Environments

Develop the associated World/Map/Environment for searching on. Should define the
spatial relationships: size, dimension, number of grid points, definition of
neighbors.

See Threat.py; A Threat can be associated with the Environment and encodes some
'cost' which is used by the searching functions.
"""
from Graph import Node, XYNode, XYTNode
import numpy as np


class Environment(object):
    """Base class for Environments

    Environments are the reference point for threats and graph generation.
    Subclasses that extend Environment should define their form in more explicit
    detail (i.e. it's number of dimensions, size, resolution, relationships
    adjacent points.)
    It should define a way to add a threat field and define a way to get the neighbors
    of a given location

    Threat fields are accessible through an Environment instance (env.threat_field)
    and can be added at the creation of an environment:
    env = Environment(dim=2, threat_field = my_field)
    OR after Environment established
    env.add_threat_field(my_field)"""

    def __init__(self, dim, threat_field=None):
        self.dim = dim
        self.threat_field = threat_field

    def get_neighbors(self, node):
        return NotImplementedError

    def add_threat_field(self, threat_field):
        self.threat_field = threat_field


class XYEnvironment(Environment):
    """This class is for 2D environments where locations are given by (x, y) points

    Generate a XY (2D) Environment example:
    env = XYEnvironment(x_size=10, y_size=10, x_pts=20, y_pts=30)
    to generate a 10 by 10 environment with resolution of 20 grid points in x direction
    and 30 grid points in y direction

    get_neighbors function uses 4-way connectivity"""

    def __init__(self, x_size, y_size, x_pts, y_pts, threat_field=None):
        super().__init__(dim=2, threat_field=threat_field)

        self.x_size = x_size
        self.y_size = y_size
        self.grid_sep_x = x_size / (x_pts - 1)
        self.grid_sep_y = y_size / (y_pts - 1)
        self.n_grid_x = x_pts
        self.n_grid_y = y_pts
        self.n_grid = self.n_grid_x * self.n_grid_y

    def get_neighbors(self, node):
        neighbors = []  # neighbors is a list of Nodes
        curr_id = node.node_id
        # Add neighbor to the RIGHT
        if (curr_id + 1 < self.n_grid) and ((curr_id + 1) % self.n_grid_x != 0):
            new_id = curr_id + 1
            new_node = XYNode(new_id)
            mx = new_id % self.n_grid_x
            my = int(new_id / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            neighbors.append(new_node)
        # Add neighbor to the LEFT
        if (curr_id - 1 >= 0) and (curr_id % self.n_grid_x != 0):
            new_id = curr_id - 1
            new_node = XYNode(new_id)
            mx = new_id % self.n_grid_x
            my = int(new_id / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            neighbors.append(new_node)
        # Add neighbor ABOVE
        if curr_id + self.n_grid_x < self.n_grid:
            new_id = curr_id + self.n_grid_x
            new_node = XYNode(new_id)
            mx = new_id % self.n_grid_x
            my = int(new_id / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            neighbors.append(new_node)
        # Add neighbor BELOW
        if curr_id - self.n_grid_x >= 0:
            new_id = curr_id - self.n_grid_x
            new_node = XYNode(new_id)
            mx = new_id % self.n_grid_x
            my = int(new_id / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            neighbors.append(new_node)
        return neighbors

    def get_location_from_gridpt(self, gridpt):
        """Get an x, y location from a grid point id number

        x, y = env.get_location_from_gridpt(5)"""
        mx = gridpt % self.n_grid_x
        my = int(gridpt / self.n_grid_x)
        pos_x = mx * self.grid_sep_x
        pos_y = my * self.grid_sep_y
        return pos_x, pos_y

    def get_gridpt_from_location(self, pos_x, pos_y):
        """Get the associated grid point id from an x, y location

        grid_pt = env.get_gridpt_from_location(x_loc, y_loc)

        TODO: Check bounds of env for valid x, y locations"""
        mx = int(pos_x / self.grid_sep_x)
        my = int(pos_y / self.grid_sep_y)
        gridpt = my * self.n_grid_x + mx
        return gridpt

    def __str__(self):
        selfstring = "x_size = {0}, y_size = {1}, n_grid_x = {2}, n_grid_y = {3}".format(
            self.x_size, self.y_size, self.n_grid_x, self.n_grid_y)
        return "XYEnv: " + selfstring


class SquareXYEnvironment(XYEnvironment):
    """Simple way to define a Square XYEnvironment

    Define a strictly square environment by calling XYEnvironment constructor with
    x_size = y_size and x_pts = y_pts

    square_env = SquareXYEnvironment(wksp_size = 10, grid_pts = 20)"""

    def __init__(self, wksp_size, grid_pts, threat_field=None):
        super().__init__(x_size=wksp_size, y_size=wksp_size, x_pts=grid_pts, y_pts=grid_pts, threat_field=threat_field)


class XYTEnvironment(XYEnvironment):
    """This defines a Time-varying 2D environment, therefore locations are (x, y, t) points"""

    def __init__(self, x_size, y_size, x_pts, y_pts, t_final, t_pts, exp_cost=1,
                 wait_cost=0, move_cost=0):
        super().__init__(x_size=x_size, y_size=y_size, x_pts=x_pts, y_pts=y_pts)

        self.t_final = t_final
        self.t_pts = t_pts
        self.t_sep = t_final / t_pts
        self.exposure_cost = exp_cost
        self.wait_cost = wait_cost
        self.move_cost = move_cost
        # There are some additional considerations to think about speed with relation
        # to the density of the grid. Seems more appropriate if time step is related to
        # the grid separation. Otherwise vehicle apparent speed changes with grid size,
        # and changing grid resolution shouldn't affect vehicle speed. For SquareEnv,
        # t_step = grid_sep/speed works, but what about NonSquare Environments? Have
        # a t_step_x and t_step_y??

    def get_neighbors(self, node, wait=True):
        neighbors = []  # neighbors is a list of Nodes
        curr_id = node.node_id
        curr_id_mod = node.node_id % self.n_grid
        # Add neighbor to WAIT at current location
        if wait:
            new_id = curr_id + self.n_grid
            wait_node = XYTNode(new_id)
            wait_node.pos_x = node.pos_x
            wait_node.pos_y = node.pos_y
            wait_node.time_idx = node.time_idx + 1
            wait_node.time = wait_node.time_idx * self.t_sep
            neighbors.append(wait_node)
        # Add neighbor to the RIGHT
        if (curr_id_mod + 1 < self.n_grid) and ((curr_id_mod + 1) % self.n_grid_x != 0):
            new_id = curr_id + 1 + self.n_grid
            new_node = XYTNode(new_id)
            mx = new_id % self.n_grid_x
            my = int((new_id % self.n_grid) / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            new_node.time_idx = node.time_idx + 1
            new_node.time = new_node.time_idx * self.t_sep
            neighbors.append(new_node)
        # Add neighbor to the LEFT
        if (curr_id_mod - 1 >= 0) and (curr_id_mod % self.n_grid_x != 0):
            new_id = curr_id - 1 + self.n_grid
            new_node = XYTNode(new_id)
            mx = new_id % self.n_grid_x
            my = int((new_id % self.n_grid) / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            new_node.time_idx = node.time_idx + 1
            new_node.time = new_node.time_idx * self.t_sep
            neighbors.append(new_node)
        # Add neighbor ABOVE
        if curr_id_mod + self.n_grid_x < self.n_grid:
            new_id = curr_id + self.n_grid_x + self.n_grid
            new_node = XYTNode(new_id)
            mx = new_id % self.n_grid_x
            my = int((new_id % self.n_grid) / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            new_node.time_idx = node.time_idx + 1
            new_node.time = new_node.time_idx * self.t_sep
            neighbors.append(new_node)
        # Add neighbor BELOW
        if curr_id_mod - self.n_grid_x >= 0:
            new_id = curr_id - self.n_grid_x + self.n_grid
            new_node = XYTNode(new_id)
            mx = new_id % self.n_grid_x
            my = int((new_id % self.n_grid) / self.n_grid_x)
            new_node.pos_x = mx * self.grid_sep_x
            new_node.pos_y = my * self.grid_sep_y
            new_node.time_idx = node.time_idx + 1
            new_node.time = new_node.time_idx * self.t_sep
            neighbors.append(new_node)
        return neighbors

    def get_location_from_gridpt(self, gridpt):
        """Get an x, y location and time index from a grid point id number

        x, y, t_idx = env.get_location_from_gridpt(5)"""
        mx = gridpt % self.n_grid_x
        my = int((gridpt % self.n_grid) / self.n_grid_x)
        pos_x = mx * self.grid_sep_x
        pos_y = my * self.grid_sep_y
        t_idx = int(gridpt / self.n_grid)
        return pos_x, pos_y, t_idx

    def get_gridpt_from_location(self, pos_x, pos_y, t_idx=0):
        """Get the associated grid point id from an x, y location
        If no t_idx is supplied, then the grid point returned corresponds
        to the initial time.

        grid_pt = env.get_gridpt_from_location(x_loc, y_loc)

        TODO: Check bounds of env for valid x, y locations"""
        mx = int(pos_x / self.grid_sep_x)
        my = int(pos_y / self.grid_sep_y)
        gridpt = my * self.n_grid_x + mx + t_idx * self.n_grid
        return gridpt

    def node_spatial_distance(self, node1, node2):
        """Find the Euclidean (Norm-2) distance between two nodes in the XYTEnvironment"""
        n1_vec = (node1.pos_x, node1.pos_y)
        n2_vec = (node2.pos_x, node2.pos_y)
        return np.linalg.norm(np.array(n1_vec) - np.array(n2_vec))

    def __str__(self):
        selfstring = "x_size = {0}, y_size = {1}, n_grid_x = {2}, n_grid_y = {3}, t_final = {4}".format(
            self.x_size, self.y_size, self.n_grid_x, self.n_grid_y, self.t_final)
        return "XYTEnv: " + selfstring
