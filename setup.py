import glob
import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

data_files = ["heat_sim_config.cfg", "abaqus_v6.env"] + glob.glob("case_hardening_simulation/interaction_properties/*")
data_files += glob.glob("case_hardening_simulation/compiled_subroutines/*.o")
materials = glob.glob('case_hardening_simulation/materials/dante_3/USR/*')
for material in materials:
    data_files.extend(glob.glob(material + "/*"))
for i, data_file in enumerate(data_files):
    if data_file.startswith("case_hardening_simulation/"):
        data_files[i] = data_file.replace("case_hardening_simulation/", "")

setup(name="case_hardening_simulation",
      version="0.0.1",
      description="python package for simulating fatigue properties of case hardened components",
      long_description=README,
      long_description_content_type="text/markdown",
      install_requires=["numpy", "abaqus_python", "input_file_reader"],
      author="Erik Olsson",
      author_email="erolsson@kth.se",
      packages=["case_hardening_simulation"],
      package_data={"case_hardening_simulation": data_files},
      entry_points={"console_scripts":
                    ["case_hardening_simulation=case_hardening_simulation.__main__:main"]}
      )
