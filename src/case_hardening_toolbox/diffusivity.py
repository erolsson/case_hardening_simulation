import numpy as np


def lee_matlock_tyne(temp, carbon, material):
    carbon = 100*carbon
    mn = material.get('Mn', 0)
    cr = material.get('Cr', 0)
    si = material.get('Si', 0)
    ni = material.get('Ni', 0)
    mo = material.get('Mo', 0)
    al = material.get('Al', 0)

    D0 = 0.146 - 0.036*carbon*(1 - 1.075*cr) + mn*-0.0315 + si*0.0509 + ni*-0.0085 + mo*0.3031 + al*-0.0520
    E0 = 144.3 - 15.0*carbon + 0.37*carbon**2 + mn*-4.3663 + si*4.0507 + ni*-1.2407 + mo*12.1266 + al*-6.7886 + \
        cr*7.7260
    return D0*np.exp(-E0/8.314E-3/(temp+273))*100


def read_composition_file(composition_filename):
    """

    :param composition_filename:    Path to the file containing composition data
    :return: A dict with the compositions in wt%
    """
    with open(composition_filename, 'r') as composition_file:
        file_lines = composition_file.readlines()
        composition = {}
        for line in file_lines:
            if not line.startswith('**'):
                try:
                    element, data = line.split(':')
                    composition[element] = float(data)
                except ValueError:
                    raise ValueError("Data must be on the form element: wt&")
    return composition


def write_diffusion_file(filename, material):
    """
    Function for creating a file controlling carbon diffusion in Dante simulations
    The diffusion model is taken from Lee, Matlock and Tyne, An Empirical Model for Carbon Diffusion in Austenite
    Incorporating Alloying Elements, ISIJ International, Vol 51(11), pp. 1903-1911, 2011

    :param filename: Filename of the created diffusion file for Dante.
    :param material: A dict with the composition of the material of layout {'Element': wt%} where element is the
                     notation used in the periodic system. If an element needed in the model is not provided
                     it is assumed that its wt% is 0 in the material
    :return:         Nothing
    """
    file_lines = []
    carbon = np.arange(0.002, 0.012, 0.0005)
    temperature = np.arange(750, 1150, 10)

    for temp in temperature:
        for carb in carbon:
            file_lines.append('\t' + str(lee_matlock_tyne(temp, carb, material)) + ', ' + str(carb) + ', ' + str(temp))

    with open(filename, 'w') as diffusion_file:
        for line in file_lines:
            diffusion_file.write(line + '\n')
        diffusion_file.write('**EOF')
