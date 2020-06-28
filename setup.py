import setuptools

import codecs
import os.path

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

long_description = read("README.md")

setuptools.setup(
    name="timetemp3",
    version=get_version("timetemp3/__init__.py"),
    author="David Crook",
    author_email="idcrook@users.noreply.github.com",
    description="Display time/temperature on Raspberry Pi and log to cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/idcrook/timetemp3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Topic :: Home Automation",
        "Environment :: Console"
    ],
    python_requires='>=3.6',
    install_requires=[
        # 'geojson>=2.5.0',  # missing implicit dependency in pyowm develop/v3 branch
        'python-nest>=4.1.0',
        # 'psutil',
        # 'click', 
        'Adafruit_BMP @ git+https://github.com/adafruit/Adafruit_Python_BMP.git@master#egg=Adafruit_BMP-1.5.2',
        'Adafruit_LED_Backpack @ git+https://github.com/adafruit/Adafruit_Python_LED_Backpack.git@master#egg=Adafruit_LED_Backpack-1.8.1',
        'phant3 @ https://github.com/idcrook/python3-phant.git@master#egg=phant3-0.1.0',
        'pyowm @ git+https://github.com/csparpa/pyowm.git@develop#egg=pyowm-3.0.0',
    ],
    entry_points={
        'console_scripts': [
            'timetemp_7segment_clock=timetemp3.my_7segment_clock:main',
            'timetemp_weather_logging=timetemp3.my_weather_logging:main',
        ],
    },
)

""" 
 - https://packaging.python.org/tutorials/packaging-projects/#packaging-your-project
 - https://packaging.python.org/guides/distributing-packages-using-setuptools/
 - https://packaging.python.org/guides/single-sourcing-package-version/
"""