import pathlib
import sys

package_directory = pathlib.Path(__file__).parents[1].absolute()


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
    return config_dict


config_data = get_config_data()
abq = config_data["abaqus"]
dante_umat = pathlib.Path(config_data["dante_umat"]).expanduser()
dante_material_library = pathlib.Path(config_data["dante_material_library"]).expanduser()
python = sys.executable

if __name__ == '__main__':
    print(package_directory)
    print(abq)
    print(dante_umat)
    print(dante_material_library)
    print(python)
