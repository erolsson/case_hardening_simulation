import glob
import os
import pathlib
import re
import shutil
import subprocess

import numpy as np
from case_hardening_simulation.display_functions import list_interaction_properties
from case_hardening_simulation.case_hardening_toolbox import CaseHardeningToolbox


class HeatTreatmentFileReadingError(ValueError):
    pass


def check_interaction_property(medium):
    implemented_int_properties = list_interaction_properties()
    if medium not in implemented_int_properties:
        list_of_int_prop_strings = ["\t" + int_prop + "\n" for int_prop in implemented_int_properties]
        list_of_int_prop_strings = ''.join(list_of_int_prop_strings)
        print("The interaction property " + medium + " is not implemented\n",
              "Currently implemented interaction properties are:\n" + list_of_int_prop_strings)
        raise ValueError
    return medium


class KeywordData:
    def __init__(self, parameters):
        self.parameters = parameters
        self.data = []


class CoolingStepData:
    def __init__(self, data_line):
        data_line = re.sub(r"[\n\t\s]*", "", data_line)   # Trim all whitespace
        try:
            name, time, temperature, medium = data_line.split(",")
            self.step_name = name
            self.time = float(time)*60
            self.temperature = float(temperature)
            self.interaction_property = check_interaction_property(medium)

        except ValueError:
            raise ValueError("The cooling data has to be on the form\n"
                  "\tstep_name,\ttime,\ttemperature,\tcooling_medium")


class HeatTreatmentData:
    """
    This class reads the heat treatment file and stores the data to setup the heat treatment simulations
    """
    def __init__(self, heat_treatment_filename):
        key_words = parse_heat_simulation_file(heat_treatment_filename)

        def read_keyword_parameter(keyword, parameter_name):
            try:
                return key_words[keyword].parameters[parameter_name]
            except KeyError:
                raise ValueError("The", parameter_name, "is a mandatory parameter for the keyword", '*' + keyword)

        def read_keyword_data(keyword):
            data = key_words[keyword].data
            if not len(data):
                raise ValueError("Data lines are mandatory to the keyword", "*" + keyword)
            return data

        def read_optional_parameter(keyword, parameter_name, default=None):
            try:
                return read_keyword_parameter(keyword, parameter_name)
            except ValueError:
                return default

        self.simulation_directory = pathlib.Path(read_keyword_parameter("simulation_directory", "directory"))
        odb_directory = read_optional_parameter("odb_directory", "directory", self.simulation_directory)
        self.odb_directory = pathlib.Path(odb_directory).expanduser()
        self.simulation_directory = self.simulation_directory.expanduser()
        self.input_filename = pathlib.Path(read_keyword_parameter("model_file", "filename")).expanduser()
        if not self.input_filename.is_file():
            raise ValueError("The specified input file ", self.input_filename, "does not exist!")

        self.bc_filename = pathlib.Path(read_keyword_parameter("bc_file", "filename")).expanduser()
        if not self.bc_filename.is_file():
            raise ValueError("The specified bc file ", self.bc_filename, "does not exist!")

        self.name = read_keyword_parameter("simulation_name", "name")

        self.include_file_directory = pathlib.Path(read_optional_parameter("include_file_directory", "directory",
                                                                           self.simulation_directory))
        self.include_file_name = read_optional_parameter("include_file_name", "name", self.name)
        self.material = read_keyword_parameter("material", "dante_material_name")
        self.initial_carbon = read_optional_parameter("initial_carbon", "carbon", None)

        # Processing the carburization data
        carbon_potential = read_keyword_data("carbon_potential")
        self.carbon_potential = np.zeros((len(carbon_potential), 2))
        for i, c_data in enumerate(carbon_potential):
            self.carbon_potential[i] = [float(val) for val in c_data.rstrip().lstrip().split(',')]
        self.carbon_potential[:, 0] *= 60     # Set time in seconds
        self.carbon_potential[:, 1] /= 100    # Set carbon in fraction, not wt%

        carburization_temperature = read_keyword_data("carburization_temperature")
        self.carburization_temperature = np.zeros((len(carburization_temperature), 2))
        for i, c_data in enumerate(carburization_temperature):
            self.carburization_temperature[i] = [float(val) for val in c_data.rstrip().lstrip().split(',')]
        self.carburization_temperature[:, 0] *= 60  # Set time in seconds

        carburization_bcs = ["carbon_potential", "mass_transfer"]
        self.carburization_bc = read_optional_parameter("carburization_steps", "boundary_condition",
                                                        carburization_bcs[1])
        if self.carburization_bc not in carburization_bcs:
            raise ValueError("The boundary condition parameter to carburization steps has to be either [" +
                             ", ".join(carburization_bcs) + "]")

        self.cooling_data = [CoolingStepData(cooling_line) for cooling_line in read_keyword_data("cooling")]
        if "tempering" in key_words:
            self.tempering_data = [CoolingStepData(tempering_line) for tempering_line in read_keyword_data("tempering")]
        else:
            self.tempering_data = None

        self.final_temperature = read_optional_parameter("final_temperature", "temperature",
                                                         self.carburization_temperature[-1, 1])


def parse_heat_simulation_file(heat_treatment_filename):
    """
        Reads the data provided in the heat treatment file and provide default values where data is not provided
        :param heat_treatment_filename  A path to a heat treatment file
    """

    required_keywords = [
        "model_file",
        "bc_file",
        "carburization_temperature",
        "carbon_potential",
        "simulation_directory",
        "simulation_name"]

    keywords = {}
    keyword = None

    with open(heat_treatment_filename) as heat_treatment_file:
        file_lines = heat_treatment_file.readlines()
        for i, line in enumerate(file_lines, 1):
            line = line.replace(' ', '').rstrip()
            if not line.startswith('**') and len(line):
                line = line.replace(' ', '').rstrip()
                words = line.split(',')
                if line.startswith('*'):
                    keyword = words[0][1:].lower()
                    parameters = words[1:]
                    if keyword in keywords:
                        raise HeatTreatmentFileReadingError("The keyword \n\t*{0}\n appears more than one time in the "
                                                            "file {1}".format(keyword, heat_treatment_filename))
                    parameter_dict = {}
                    for parameter in parameters:
                        par_words = parameter.split("=")
                        parameter_dict[par_words[0]] = par_words[1]
                    keywords[keyword] = KeywordData(parameter_dict)
                elif keyword is not None:
                    keywords[keyword].data.append(line)
                else:
                    raise HeatTreatmentFileReadingError("The data line \n\t{0} \ncannot appear at line {1} of the "
                                                        "file".format(line, i))
    missing = []
    for req_keyword in required_keywords:
        if req_keyword not in keywords:
            missing.append(req_keyword)
    if len(missing):
        error_string = "The keyword(s)\n"
        for missing_keyword in missing:
            error_string += "\t*" + missing_keyword + "\n"
        error_string += "is(are) mandatory in the heat treatment file"
        raise HeatTreatmentFileReadingError(error_string)
    return keywords


def create_heat_treatment_simulation(heat_treatment_filename, cpus, run, config_file=None):
    """
    :param heat_treatment_filename: path to the filename that defines the heat treatment simulation
    :param cpus:                    Number of cpus used for running the simulation
    :param run                      Bool setting if the simulation should be run or just written
    :param config_file              path to the file configuring heat treatment simulations. If None, the package
                                    config file is used
    :return:
    """
    parameters = HeatTreatmentData(heat_treatment_filename)
    toolbox = CaseHardeningToolbox(parameters, config_filename=config_file)
    toolbox.write_files(cpus)

    if run:
        current_directory = os.getcwd()
        os.chdir(parameters.simulation_directory)
        chmod = subprocess.Popen("chmod u+x run_heat_treatment_sim.sh", cwd=os.getcwd(), shell=True)
        chmod.wait()
        heat_sim_process = subprocess.Popen("./run_heat_treatment_sim.sh", cwd=os.getcwd(), shell=True)
        heat_sim_process.wait()
        os.chdir(current_directory)

        if parameters.odb_directory != parameters.simulation_directory:
            if not parameters.odb_directory.is_dir():
                parameters.odb_directory.mkdir(parents=True)
            odb_files = glob.glob(str(parameters.simulation_directory) + "/*.odb")
            odb_files = [pathlib.Path(odb_file) for odb_file in odb_files]
            for odb_file in odb_files:
                shutil.move(odb_file, parameters.odb_directory / odb_file.name)
