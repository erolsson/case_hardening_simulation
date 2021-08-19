import pathlib
import sys

package_directory = pathlib.Path(__file__).parents[0].absolute()


class Config:
    def __init__(self, config_dict):
        self.abq = config_dict["abaqus"]
        self.dante_umat = pathlib.Path(config_dict["dante_umat"]).expanduser()
        self.dante_material_library = pathlib.Path(config_dict["dante_material_library"]).expanduser()
        self.python = sys.executable


def get_config_data(config_filename=package_directory / 'heat_sim_config.cfg'):
    config_dict = {}
    with open(config_filename, 'r') as config_file:
        config_lines = config_file.readlines()
        for line in config_lines:
            try:
                keyword, data = line.split('=')
            except ValueError:
                raise ValueError("config data must be on the form *keyword=data")
            if keyword.startswith('*') and not keyword.startswith('**'):
                config_dict[keyword[1:]] = data.rstrip()
    return Config(config_dict)
