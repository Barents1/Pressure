from setuptools import setup, find_packages

setup(
    name="pressure",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt5>=5.15.10",
        "pyserial>=3.5",
        "numpy>=2.1.1",
        "scipy>=1.14.0",
        "nidaqmx>=1.0.1",,
        "PyDAQmx>=1.4.6",
    ],
    entry_points={
        "console_scripts": [
            "pressure=main:main"
        ],
    },
    package_data={
        "": ["*.png","*.txt"],
    },
)