"""Test out Threat and threat field classes"""

from Threat import GaussDynamicThreat, GaussDynamicThreatField
from Environment import XYTEnvironment
import math
import matplotlib.pyplot as plt
from Visualize import animate_threat_field, animate_test, animate_threat_field_2D


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

    print(threat_field.threats)
    print(threat_field.threats[0])

    for idx, threat in enumerate(threat_field.threats):
        print("Threat ", idx, ", Location ", threat_field.threats[idx].location)

    for threat in range(len(threat_field.threats)):
        print(threat_field.threats[threat])

    sensor_loc = (3, 3)
    sense_time = 1
    threat_val = threat_field.threat_value(x=sensor_loc[0], y=sensor_loc[1], t=sense_time)

    print("Threat at sensor location: ", sensor_loc, " t = ", sense_time, " : ", threat_val)

    # dynamic_anim = animate_threat_field(env=env, threat_field=threat_field)
    # dynamic_anim.save('dynamic_field_01.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
    # animate_test()

    anim_2d = animate_threat_field_2D(env=env, threat_field=threat_field)
    plt.show()


if __name__ == "__main__":
    main()