import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
# pass
setup(name="case_hardening_simulations",
      version="0.0.1",
      description="python package for simulating fatigue properties of case hardened components",
      long_description=README,
      long_description_content_type="text/markdown",
      install_requires=["numpy", "abaqus_python", "input_file_reader"],
      author="Erik Olsson",
      author_email="erolsson@kth.se",
      packages=["case_hardening_toolbox"],
      include_package_data=True,
      entry_points={"console_scripts": ["case_hardening_simulation=case_hardening_toolbox.__main__:main"]}
      )
