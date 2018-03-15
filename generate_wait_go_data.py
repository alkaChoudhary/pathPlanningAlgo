from Threat import GaussDynamicThreatField
from Environment import XYTEnvironment
from DataManagement import DataCollector, SimData
from Graph import XYTNode, Vertex, Graph
from Search import reconstruct_path, TimeAstar
from timeit import default_timer


def main():
    t_final = 10
    env = XYTEnvironment(x_size=10, y_size=10, x_pts=10, y_pts=10, t_final=t_final, t_pts=100)

    my_collector = DataCollector(filename='test_data', sim_folder='first_test')

    for sim_n in range(50):
        print("--------------------------------------------------------------------")
        print("Sim ", sim_n)
        threat_field = GaussDynamicThreatField(offset=2)
        threat_field.generate_random_field(env=env, n_threats=None, fixed_shape=False,
                                       fixed_intensity=False, fixed_location=False)
        env.add_threat_field(threat_field)
        print("\nEnv.threat_field: ", env.threat_field)

        # Use first node in the environment as start node
        start_x, start_y, tidx0 = env.get_location_from_gridpt(0)
        start_node = XYTNode(node_id=0, pos_x=start_x, pos_y=start_y, time_idx=tidx0)

        # Use last node in environment as goal node
        goal_x, goal_y, goal_tidx = env.get_location_from_gridpt(env.n_grid - 1)
        goal_node = XYTNode(node_id=env.n_grid - 1, pos_x=goal_x, pos_y=goal_y, time_idx=goal_tidx)

        time_window = (0, t_final)
        print("time window = ", time_window)

        # Assign Exposure, Movement, Waiting Costs
        env.exposure_cost = 1
        env.move_cost = 1
        env.wait_cost = 0

        # ------------------------- Waiting Search Setup ------------------------------------------
        # Create the Graph based on our environment
        graph_wait = Graph(env=env)

        # Add a start vertex to the graph to begin the search at. Add goal vertex for search
        graph_wait.add_vertex(start_node)
        start_vertex = graph_wait.get_vertex(start_node)
        goal_vertex = Vertex(node=goal_node)

        print("\nRun A* Waiting search")
        start_wait = default_timer()
        goal_vertex_wait = TimeAstar(graph=graph_wait, start_vertex=start_vertex, goal_vertex=goal_vertex,
                                     time_window=time_window, wait=True)
        wait_time = default_timer() - start_wait
        print("A*-Wait finished in ", wait_time, " seconds")
        path_wait = [goal_vertex_wait.node]
        reconstruct_path(goal_vertex_wait, path_wait)
        path_wait.reverse()

        # ------------------------- No-Waiting Search section --------------------------------------------
        print("\nRun A* No-Waiting search")
        graph_nowait = Graph(env=env)
        graph_nowait.add_vertex(start_node)
        start_vertex_nw = graph_nowait.get_vertex(start_node)
        goal_vertex_nw = Vertex(node=goal_node)

        start_nowait = default_timer()
        goal_vertex_nowait = TimeAstar(graph=graph_nowait, start_vertex=start_vertex_nw, goal_vertex=goal_vertex_nw,
                                       time_window=time_window, wait=False)
        nowait_time = default_timer() - start_nowait
        print("A*-NoWait finished in ", nowait_time, " seconds")
        path_nowait = [goal_vertex_nowait.node]
        reconstruct_path(goal_vertex_nowait, path_nowait)
        path_nowait.reverse()

        # Store simulation data and add to data collector
        nsim_data = SimData(sim_n)
        nsim_data.path_costs["wait"] = goal_vertex_wait.g_cost
        nsim_data.path_costs["no_wait"] = goal_vertex_nowait.g_cost
        nsim_data.paths["wait"] = path_wait
        nsim_data.paths["no_wait"] = path_nowait
        nsim_data.compute_time["wait"] = wait_time
        nsim_data.compute_time["no_wait"] = nowait_time
        nsim_data.env_data["n_threats"] = threat_field.n_threats
        nsim_data.env_data["x_size"] = env.x_size
        nsim_data.env_data["y_size"] = env.y_size
        nsim_data.env_data["x_pts"] = env.n_grid_x
        nsim_data.env_data["y_pts"] = env.n_grid_y
        nsim_data.env_data["t_final"] = t_final
        nsim_data.env_data["t_pts"] = env.t_pts
        nsim_data.env_data["exposure_cost"] = env.exposure_cost
        nsim_data.env_data["move_cost"] = env.move_cost
        nsim_data.env_data["wait_cost"] = env.wait_cost
        nsim_data.threats = threat_field.threats

        my_collector.add_sim(nsim_data)
        # End of current simulation
    my_collector.write_to_file()
    print("\nDone with simulation runs!!")


if __name__ == "__main__":
    main()
