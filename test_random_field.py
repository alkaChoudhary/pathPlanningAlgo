from Threat import GaussDynamicThreat, GaussDynamicThreatField
from Environment import XYTEnvironment
import matplotlib.pyplot as plt
from Visualize import animate_threat_field
import os
import errno


def main():
    t_final = 10
    env = XYTEnvironment(x_size=10, y_size=10, x_pts=10, y_pts=10, t_final=t_final, t_pts=40)

    threat_field = GaussDynamicThreatField(offset=2)
    # threat_field.generate_random_field(env=env)
    threat_field.generate_random_field(env=env, n_threats=5, fixed_shape=True,
                                       fixed_intensity=True)
    env.add_threat_field(threat_field)
    print("Env.threat_field: ", env.threat_field)

    anim = animate_threat_field(env=env, threat_field=threat_field)

    the_folder = "Videos"
    try:
        os.makedirs(the_folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    save_file = the_folder + '/' + 'random_threat.mp4'

    vid_length = 5  # seconds
    fps = env.t_pts / vid_length

    anim.save(save_file, writer='ffmpeg', fps=fps)

    plt.show()


if __name__ == "__main__":
    main()