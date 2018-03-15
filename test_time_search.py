"""Test out Threat and threat field classes"""

from Threat import GaussDynamicThreat, GaussDynamicThreatField
from Environment import XYTEnvironment
import matplotlib.pyplot as plt
from Visualize import draw_threat_field, draw_threat_field_2D, draw_path, animate_threat_field_2D
from Graph import XYTNode, Vertex, Graph
from Search import Astar, reconstruct_path, TimeAstar


def main():
    t_final = 10
    env = XYTEnvironment(x_size=10, y_size=10, x_pts=10, y_pts=10, t_final=t_final, t_pts=40)

    threat1 = GaussDynamicThreat(location_0=(2, 2), shape_0=(0.5, 0.5), intensity_0=2)
    threat1.set_rates_by_start_end(location_0=(8, 8), shape_0=(0.5, 0.5), intensity_0=5,
                                   location_f=(2, 2), shape_f=(0.1, 0.1), intensity_f=2, t_final=t_final)
    threat2 = GaussDynamicThreat(location_0=(8, 8), shape_0=(1.0, 1.0), intensity_0=10)
    threat2.set_rates(location_rate=(0, -0.5), shape_rate=(0.1, 0.1), intensity_rate=-0.2)
    threat3 = GaussDynamicThreat(location_0=(0, 0), shape_0=(0.25, 0.25), intensity_0=5)
    threat4 = GaussDynamicThreat(location_0=(10, 0), shape_0=(0.25, 0.25), intensity_0=5)
    threat5 = GaussDynamicThreat(location_0=(0, 10), shape_0=(0.25, 0.25), intensity_0=5)
    threat6 = GaussDynamicThreat(location_0=(0, 5), shape_0=(0.25, 0.25), intensity_0=5)
    threats = [threat1, threat2, threat3, threat4, threat5, threat6]
    threat_field = GaussDynamicThreatField(threats=threats, offset=2)

    env.add_threat_field(threat_field)
    print("Env.threat_field: ", env.threat_field)

    node_list = {}
    for gridpt in range(env.n_grid * env.t_pts):
        mx = gridpt % env.n_grid_x
        my = int((gridpt % env.n_grid) / env.n_grid_x)
        new_node = XYTNode(node_id=gridpt)
        new_node.pos_x = mx * env.grid_sep_x
        new_node.pos_y = my * env.grid_sep_y
        new_node.time_idx = int(gridpt / env.n_grid)
        new_node.time = new_node.time_idx * env.t_sep
        node_list[gridpt] = new_node
        print(new_node)

    graph = Graph(env=env)
    graph.add_vertex(node_list[0])
    start_vertex = graph.get_vertex(node_list[0])
    print("Start vertex: ", start_vertex)

    neighbor_list = graph.env.get_neighbors(start_vertex.node)
    print("neighbor_list")
    print(neighbor_list)
    for nbr in neighbor_list:
        print(nbr)
        graph.add_edge(start_vertex.node, nbr, 1.0)

    for neighbor in start_vertex.neighbors:
        print(neighbor)

    goal_vertex = Vertex(node=node_list[env.n_grid * env.t_pts - 1])
    print("goal node = ", goal_vertex.node)

    time_window = (0, t_final)
    print("time window = ", time_window)

    # Assign Exposure, Movement, Waiting Costs
    env.exposure_cost = 1
    env.move_cost = 1
    env.wait_cost = 0

    print(graph)

    print("Run A* search")
    goal_vertex_found = TimeAstar(graph=graph, start_vertex=start_vertex, goal_vertex=goal_vertex,
                                  time_window=time_window, wait=False)
    print(goal_vertex_found)

    path = [goal_vertex_found.node]
    reconstruct_path(goal_vertex_found, path)
    path.reverse()
    print("Path found :")
    for waypoint in path:
        print(waypoint)
    print("Path Cost = ", goal_vertex_found.g_cost)

    anim_2d = animate_threat_field_2D(env=env, threat_field=threat_field, path=path)

    plt.show()


if __name__ == "__main__":
    main()
