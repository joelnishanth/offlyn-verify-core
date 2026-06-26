from setuptools import find_packages, setup
import os
from glob import glob

package_name = "rover_sim"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "worlds"), glob("worlds/*.world")),
        (os.path.join("share", package_name, "urdf"), glob("urdf/*.urdf")),
        (os.path.join("share", package_name, "models"), glob("models/**/*", recursive=True)),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Joel Nishanth",
    maintainer_email="joel@offlyn.ai",
    description="Rover simulation for Offlyn Verify Core Phase 1",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "autonomy_planner = rover_sim.autonomy_planner:main",
        ],
    },
)
