import pathlib
import sys

import numpy as np

from abaqus_python.abaqus_interface import ABQInterface

from utilities.config import abq
from common import heat_sim_fields

abq_interface = ABQInterface(abq)


def write_stresses_to_file(sim_name, step):
    odb_file = pathlib.Path(sim_name + '.odb').absolute()
    stress, _, element_labels = abq_interface.read_data_from_odb('S', odb_file, step_name=step,
                                                                 get_position_numbers=True)
    num_points = stress.shape[0]
    gauss_point_counter = 1
    gp = []
    for i, e in enumerate(element_labels):
        if i != 0 and element_labels[i-1] == e:
            gauss_point_counter += 1
        else:
            gauss_point_counter = 1
        gp.append(gauss_point_counter)

    data = np.zeros((num_points, stress.shape[1] + 2 + len(heat_sim_fields)))

    data[:, 0] = element_labels
    data[:, 1] = gp
    data[:, 2:2+stress.shape[1]] = stress
    for i, field_var in enumerate(heat_sim_fields):
        field = abq_interface.read_data_from_odb('SDV_' + field_var, odb_file, step_name=step)
        data[:, 2+stress.shape[1] + i] = field

    fmt = '%d, %d' + ', %f'*(data.shape[1] - 2)
    np.savetxt(sim_name + '.htd', data, fmt=fmt, delimiter=',')


if __name__ == '__main__':
    simulation_name = 'Toolbox_' + sys.argv[-1]
    write_stresses_to_file(simulation_name, step=None)
