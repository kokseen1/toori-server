# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
import pathlib
import subprocess

__version__ = "1.1.3"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

ext_modules = []

if "libtins" in subprocess.run(
    ["ldconfig", "-p"], stdout=subprocess.PIPE
).stdout.decode("utf-8"):
    ext_modules.append(
        Pybind11Extension(
            "_iro",
            ["iro/main.cpp"],
            # Example: passing in the version to the compiled code
            # define_macros=[("VERSION_INFO", __version__)],
            libraries=["tins"],
        ),
    )

setup(
    name="toori-server",
    version=__version__,
    url="https://github.com/kokseen1/Iro",
    description="Server for a minimal layer 3 tunnel over http(s).",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    # extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    data_files=[
        (
            "iro",
            [
                "iro/main.cpp",
            ],
        )
    ],
    include_package_data=True,
    packages=["iro"],
    package_dir={
        "iro": "iro",
    },
    entry_points={
        "console_scripts": [
            "iro = iro.console:main",
        ]
    },
    install_requires=[
        "python-socketio",
        "scapy",
        "sanic",
    ],
)
