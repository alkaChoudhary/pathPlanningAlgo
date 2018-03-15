"""Evaluate the DataManagement classes/functions"""

from Threat import GaussDynamicThreat, GaussDynamicThreatField
from Environment import XYTEnvironment
from DataManagement import SimData, DataCollector, DataReader


def main():
    t_final = 10
    # env = XYEnvironment(x_size=10, y_size=10, x_pts=20, y_pts=20)
    env = XYTEnvironment(x_size=10, y_size=10, x_pts=20, y_pts=20, t_final=t_final, t_pts=100)

    threat1 = GaussDynamicThreat(location_0=(2, 2), shape_0=(0.5, 0.5), intensity_0=2)
    threat1.set_rates_by_start_end(location_0=(2, 2), shape_0=(0.5, 0.5), intensity_0=2,
                                   location_f=(8, 8), shape_f=(0.1, 0.1), intensity_f=10, t_final=t_final)
    threat2 = GaussDynamicThreat(location_0=(8, 8), shape_0=(1.0, 1.0), intensity_0=10)
    threat2.set_rates(location_rate=(0, -0.5), shape_rate=(0.1, 0.1), intensity_rate=-1)
    threats = [threat1, threat2]
    threat_field = GaussDynamicThreatField(threats=threats, offset=2)

    env.add_threat_field(threat_field)
    print("Env.threat_field: ", env.threat_field)

    sim1 = SimData(1)
    sim1.threats = threats
    sim1.path_costs["no_wait"] = 20
    sim1.path_costs["wait"] = 30
    sim1.compute_time["no_wait"] = 1.45
    sim1.compute_time["wait"] = 2.33

    sim2 = SimData(2)
    sims = [sim1, sim2]

    my_collector = DataCollector(filename='whatever', sim_folder='test')
    my_collector.add_sim(sim1)
    my_collector.add_sim(sim2)
    my_collector.write_to_file()

    my_reader = DataReader()
    recover_sims = my_reader.get_data_from_prompt()

    sim1 = recover_sims[0]
    print("sim1.sim_id = ", sim1.sim_id)
    print("sim1.path_costs[no_wait] = ", sim1.path_costs["no_wait"])


if __name__ == "__main__":
    main()