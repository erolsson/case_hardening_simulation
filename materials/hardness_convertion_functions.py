import numpy as np


def HRC2HV(HRC):
    """
    Converts Rockwell hardness to Vickers Hardness
    :param HRC:     Data with Rockwell hardness, accepts both scalars and numpy arrays
    :return:        Vickers hardness, datatype the same as HRC
    """
    return (223.*HRC+14500)/(100-HRC)


def HV2HRC(HV):
    """
    Converts Vickers hardness to Rockwell Hardness
    :param HV:  Data with Vickers hardness, accepts both scalars and numpy arrays
    :return:    Rockwell hardness, datatype the same as HV
    """
    return (100.*HV - 14500)/(HV+223)


if __name__ == '__main__':
    HRC_data = np.arange(45., 65., 1.)
    for HRC in HRC_data:
        print('HRC:', HRC, '-> HV:', HRC2HV(HRC))
