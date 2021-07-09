import pathlib

from utilities.config import package_directory


def list_interaction_properties():
    files = pathlib.Path.glob(package_directory / "case_hardening_toolbox" / "interaction_properties", "*.inc")
    return [file_name.stem for file_name in files]
