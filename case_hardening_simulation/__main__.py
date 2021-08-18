import argparse
import pathlib

from case_hardening_simulation.create_heat_treatment_simulation import HeatTreatmentFileReadingError
from case_hardening_simulation.create_heat_treatment_simulation import create_heat_treatment_simulation
from case_hardening_simulation.display_functions import list_interaction_properties


def main():
    def argparse_check_path(path):
        if "=" in path:
            path = path.split("=")[1]
        path = pathlib.Path(path)
        if not path.is_file():
            raise argparse.ArgumentTypeError("{0} is not a valid path to a file".format(path))
        return path

    parser = argparse.ArgumentParser(description="Setup and possible run a heat treatment simulation with Dante")
    parser.add_argument("heat_treatment_file", type=argparse_check_path, nargs="?",
                        help="Path to the file defining the heat treatment simulation")
    parser.add_argument("-l", type=str, help="List various parameters")
    parser.add_argument("-r", type=str, help="Creates and runs the simulation", nargs="?")
    parser.add_argument("--cpus", type=int, help="Number of cpu cores used for the simulations")
    args = parser.parse_args()

    heat_treatment_file = args.heat_treatment_file
    cpus = args.cpus
    if cpus is None:
        cpus = 1
    if heat_treatment_file:
        try:
            run = not args.r
            create_heat_treatment_simulation(heat_treatment_file, cpus, run)
        except HeatTreatmentFileReadingError as e:
            print("Error in reading the heat treatment file")
            print("\t", args.heat_treatment_file.absolute())
            print(e)

    elif args.l:
        objs_to_list = args.l
        if objs_to_list == "interaction_properties":
            int_properties = list_interaction_properties()
            print("Currently implemented interaction properties")
            for int_property in int_properties:
                print("\t", int_property)
        else:
            print("Currently are only displays of")
            print("\tinteraction_properties")
            print("\tmaterials")
            print("implemented")


if __name__ == "__main__":
    main()
