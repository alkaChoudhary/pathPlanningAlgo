"""Threat

Define a Threat which is associated with an Environment and used by Search.

Associates a cost for a location in the Environment. Our common threat is a
summation of Gaussians

threat = sum( 1/sqrt(2*pi*sigma_i^2)*exp(-1/2*sigma_i^2*(x - mu_i)^2)"""
import numpy as np


class Threat(object):
    """Base class for a Threat"""

    def __init__(self):
        pass


class ThreatField(object):
    """Base class for a threat field. Can be a linear combination of Threats

    A ThreatField subclass should implement a method to add threats and a
    method to calculate the threat value. This should allow for flexibility in
    different threat basis functions."""

    def __init__(self, threats=None, num_threats=0):
        self.threats = threats
        self.n_threats = num_threats

    def __getitem__(self, item):
        return self

    def add_threat(self, threat):
        return NotImplementedError

    def threat_value(self, location):
        return NotImplementedError

    def __str__(self):
        return "ThreatField: n_threats = {0}".format(self.n_threats)


class GaussThreat(Threat):
    """A single threat in an Environment with properties of a Gaussian distribution.

    location: mean of Gaussian, typically (mean_x, mean_y)
    shape: the variance/std-dev of Gaussian, typically (sigma_x, sigma_y)
    intensity: external coefficient to scale the Gaussian

    Create a GaussThreat using:
    threat1 = GaussThreat(location=(2, 2), shape=(0.5, 0.5), intensity=5)"""

    def __init__(self, location, shape, intensity):
        super().__init__()

        self.location = location
        self.shape = shape
        self.intensity = intensity

    def __str__(self):
        selfstring = "loc = {0}, shape = {1}, intensity = {2}".format(self.location, self.shape, self.intensity)
        return "GaussThreat: " + selfstring


class GaussDynamicThreat(GaussThreat):
    """A single dynamic Gaussian threat

    attributes inherited from GaussThreat are initial, new attributes are:
    location_rate:  (mean_x_rate, mean_y_rate)
    shape_rate:     (sigma_x_rate, sigma_y_rate)
    intensity_rate: dynamic weighting of the Gaussian peak

    dyn_threat = GaussDynamicThreat(location=(2, 2), shape=(0.5, 0.5), intensity=5,
                    location_rate=(0.1, -0.1), shape_rate=(0.1, 0.0), intensity_rate=-0.1)"""

    def __init__(self, location_0, shape_0, intensity_0,
                    location_rate=(0.0, 0.0), shape_rate=(0.0, 0.0), intensity_rate=0.0):
        super().__init__(location=location_0, shape=shape_0, intensity=intensity_0)

        self.location_rate = location_rate
        self.shape_rate = shape_rate
        self.intensity_rate = intensity_rate

    def set_rates(self, location_rate, shape_rate, intensity_rate):
        self.location_rate = location_rate
        self.shape_rate = shape_rate
        self.intensity_rate = intensity_rate

    def set_rates_by_start_end(self, location_0, shape_0, intensity_0,
                    location_f, shape_f, intensity_f, t_final):
        self.location = location_0
        self.shape = shape_0
        self.intensity = intensity_0
        self.location_rate = tuple(np.subtract(location_f, location_0) / t_final)
        self.shape_rate = tuple(np.subtract(shape_f, shape_0) / t_final)
        self.intensity_rate = (intensity_f - intensity_0) / t_final

    def __str__(self):
        selfstring0 = "loc0 = {0}, shape0 = {1}, intensity0 = {2}".format(self.location, self.shape, self.intensity)
        string_loc_rate = 'loc_rate = ({:.3f}, {:.3f})'.format(*self.location_rate)
        string_shape_rate = ' shape_rate = ({:.3f}, {:.3f})'.format(*self.shape_rate)
        string_intensity_rate = ' intensity_rate = {0:.3f}'.format(self.intensity_rate)
        # selfstringrate = "loc_rate = {0}, shape_rate = {1}, intensity_rate = {2}".format(
        #     self.location_rate, self.shape_rate, self.intensity_rate)
        return "GaussDynamicThreat: " + selfstring0 + "\n" + string_loc_rate + string_shape_rate + string_intensity_rate


class GaussThreatField(ThreatField):
    """A ThreatField as a linear combination of Gaussians.

    You can create several threats and then initialize the field:
    threat1 = GaussThreat(location=(2, 2), shape=(0.5, 0.5), intensity=5)
    threat2 = GaussThreat(location=(8, 8), shape=(1.0, 1.0), intensity=5)
    threat3 = GaussThreat(location=(8, 2), shape=(1.5, 1.5), intensity=5)
    threats = [threat1, threat2, threat3]
    threat_field = GaussThreatField(threats=threats, offset=2)

    OR/AND add threats to an already constructed field
    threat4 = GaussThreat(location=(2, 8), shape=(0.5, 0.5), intensity=5)
    threat_field.add_threat(threat4)

    the threat_value functions should return the cumulative intensity at a given location"""

    def __init__(self, threats=None, offset=0):
        super().__init__()

        self.threats = threats
        self.offset = offset
        if not threats:
            self.n_threats = 0
        else:
            self.n_threats = len(threats)

    def threat_value(self, x, y):
        """Given a location, returns the threat value of the field

        this_threat_value = threat_field.threat_value(x_loc, y_loc)"""
        threat_val = self.offset
        for threat in self.threats:
            threat_val = threat_val + (threat.intensity * (1 / (2 * threat.shape[0] * threat.shape[1])) *
                                       np.exp((-1 / 2) * (
                                           ((x - threat.location[0]) ** 2) / (threat.shape[0] ** 2) +
                                           ((y - threat.location[1]) ** 2) / (threat.shape[1] ** 2))))

        return threat_val

    def add_threat(self, threat):
        """Add a new threat to the field

        threat4 = GaussThreat(location=(2, 8), shape=(0.5, 0.5), intensity=5)
        threat_field.add_threat(threat4)
        """
        if self.threats is None:
            self.threats = [threat]
        else:
            self.threats.append(threat)
        self.n_threats = self.n_threats + 1


class GaussDynamicThreatField(GaussThreatField):
    """A threat field composed of GaussDynamicThreat's

    Similar operation to GaussThreatField, except account for dynamic threat_values.
    Currently making a separate class, although I might later work it to take static
    and dynamic GaussThreats, since static is just a special case of dynamic."""

    def __init__(self, threats=None, offset=0):
        super().__init__(threats=threats, offset=offset)

    def threat_value(self, x, y, t):
        """Given a location and time, returns the threat value of the field

        this_threat_value = threat_field.threat_value(x_loc, y_loc, t)"""
        threat_val = self.offset
        for threat in self.threats:
            intensity_t = threat.intensity + threat.intensity_rate * t
            location_xt = threat.location[0] + threat.location_rate[0] * t
            location_yt = threat.location[1] + threat.location_rate[1] * t
            shape_xt = threat.shape[0] + threat.shape_rate[0] * t
            shape_yt = threat.shape[1] + threat.shape_rate[1] * t
            # print("shape_xt = {0}, shape_yt = {1}".format(shape_xt, shape_yt))
            threat_val = threat_val + (intensity_t * (1 / (2 * shape_xt * shape_yt)) *
                                       np.exp((-1 / 2) * (
                                           ((x - location_xt) ** 2) / (shape_xt ** 2) +
                                           ((y - location_yt) ** 2) / (shape_yt ** 2))))
        return threat_val

    def generate_random_field(self, env, n_threats=None, fixed_location=False, fixed_shape=False,
                              fixed_intensity=False):
        """Generate a random field.
        n_threats: specify a number of threats, or if None allow random set
        Set fixed_location = True to create stationary threats
        Set fixed_shape = True to create moving threats of fixed size
        set fixed_intensity = True to create threats that don't grow or shrink
        Or allow all False for moving, shape-shifting and variable height threats"""
        # randstate = np.random.RandomState(12345678)  # for consistent random values
        randstate = np.random.RandomState()

        min_threats = 1
        max_threats = 20
        shape_factor = 0.1
        max_intensity = 5

        if not n_threats:
            n_threats = int(randstate.randint(min_threats, max_threats, 1))

        for nt in range(min_threats, n_threats+1):
            loc0x, locfx = tuple(randstate.uniform(0, env.x_size, 2))
            loc0y, locfy = tuple(randstate.uniform(0, env.y_size, 2))
            shp0x, shpfx = tuple(randstate.uniform(0, shape_factor*env.x_size, 2))
            shp0y, shpfy = tuple(randstate.uniform(0, shape_factor*env.y_size, 2))
            int0, intf = tuple(randstate.uniform(0, max_intensity, 2))
            if fixed_location:
                locfx = loc0x
                locfy = loc0y
            if fixed_shape:
                shpfx = shp0x
                shpfy = shp0y
            if fixed_intensity:
                intf = int0
            threat = GaussDynamicThreat(location_0=(loc0x, loc0y), shape_0=(shp0x, shp0y),
                                        intensity_0=int0)
            threat.set_rates_by_start_end(location_0=(loc0x, loc0y), shape_0=(shp0x, shp0y), intensity_0=int0,
                                          location_f=(locfx, locfy), shape_f=(shpfx, shpfy), intensity_f=intf,
                                          t_final=env.t_final)
            self.add_threat(threat=threat)




