import pathlib

from case_hardening_simulation.config import package_directory


def list_interaction_properties():
    files = pathlib.Path.glob(package_directory / "case_hardening_simulation" / "interaction_properties", "*.inc")
    return [file_name.stem for file_name in files]
