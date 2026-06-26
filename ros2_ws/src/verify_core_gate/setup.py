from setuptools import find_packages, setup
import os
from glob import glob

package_name = "verify_core_gate"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools", "pydantic>=2.0", "pyyaml"],
    zip_safe=True,
    maintainer="Joel Nishanth",
    maintainer_email="joel@offlyn.ai",
    description="Offlyn Verify Core policy gate for ROS 2",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "gate_node = verify_core_gate.gate_node:main",
            "cmd_vel_interceptor = verify_core_gate.cmd_vel_interceptor:main",
        ],
    },
)
