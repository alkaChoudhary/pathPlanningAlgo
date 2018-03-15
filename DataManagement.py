"""Data Management

Need to support writing search and field data to files and some ability to
read back files and generate statistics and other analysis.

Possibly using JSON format, which seems easy in Python
http://stackabuse.com/reading-and-writing-json-to-a-file-in-python/"""

# TODO: Create a class to handle analyzing data, or at least some scripts
import dill
import datetime
import errno
import os
from tkinter.filedialog import askopenfilename


class DataCollector:
    """DataCollector

    This class collects data for a set of runs during a simulation.

    Functions:
    - add_entry: add a entry to the data dictionary
    - write_to_file: finally output the data to a specified outfile"""

    def __init__(self, filename, sim_folder=''):
        self.sim_data = []
        self.top_data_folder = "Simulation_data"
        self.sim_sub_folder = sim_folder
        self.filename = filename + ".pkl"
        self.curr_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def add_sim(self, sim):
        self.sim_data.append(sim)

    def add_multiple_sims(self, sims):
        self.sim_data.extend(sims)

    def write_to_file(self):
        the_folder = self.top_data_folder + '/' + self.sim_sub_folder + 'On' + self.curr_time + '/'
        try:
            os.makedirs(the_folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        full_file = the_folder + self.filename
        with open(full_file, 'wb') as f:
            dill.dump(self.sim_data, f)


class DataReader:
    """DataReader

    Currently very simple. Get data from file and return to caller

    get_data_from_prompt"""

    def __init__(self):
        self.sim_data =[]
        self.file_location = ''

    def get_data_from_prompt(self):
        pickle_file = askopenfilename()

        with open(pickle_file, 'rb') as f:
            recover_sims = dill.load(f)
        self.sim_data = recover_sims
        self.file_location = pickle_file

        return recover_sims


class SimData:
    """SimData

    A SimData object stores all relevant information for one simulation run"""

    def __init__(self, sim_id):
        self.sim_id = sim_id
        self.path_costs = {"no_wait": 0, "wait": 0, "wait_heuristic": 0}
        self.paths = {"no_wait": None, "wait": None, "wait_heuristic": None}
        self.num_nodes_gen = {"no_wait": 0, "wait": 0, "wait_heuristic": 0}
        self.compute_time = {"no_wait": 0, "wait": 0, "wait_heuristic": 0}
        self.env_data = {"n_threats": 0, "x_size": 0, "y_size": 0, "x_pts": 10, "y_pts": 0,
                         "t_final": 0, "t_pts": 0, "exposure_cost": 0, "move_cost": 0, "wait_cost": 0}
        self.threats = None
        self.wait_label = None  # "wait" or "go"
