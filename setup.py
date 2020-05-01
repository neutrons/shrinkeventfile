import os
import versioneer
from setuptools import setup, find_packages

THIS_DIR = os.path.dirname(__file__)

def read_requirements_from_file(filepath):
    '''Read a list of requirements from the given file and split into a
    list of strings. It is assumed that the file is a flat
    list with one requirement per line.
    :param filepath: Path to the file to read
    :return: A list of strings containing the requirements
    '''
    with open(filepath, 'r') as req_file:
        return req_file.readlines()

req_filename = os.path.join(THIS_DIR, 'requirements.txt')
install_requires=read_requirements_from_file(req_filename)

req_dev_filename = os.path.join(THIS_DIR, 'requirements-dev.txt')
test_requires=read_requirements_from_file(req_dev_filename)

print(test_requires)
extras = {
    'test': test_requires,
}

setup(
    name="shrinkeventfile",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="ShrinkEventFile",
    long_description="Shrink NeXuS Neutron Event Files",
    author="Pete Peterson + Marshall McDonnell",
    url="https://github.com/neutrons/shrinkeventfile",
    project_urls={
        "Source Code": "https://github.com/neutrons/shrinkeventfile",
    },
    entry_points={
        'console_scripts': [
            "shrinkeventfile = shrinkeventfile.shrinkeventfile:main",
        ]
    },
    packages=find_packages(),
    install_requires=install_requires,
    test_suite='tests',
    tests_require=test_requires,
    extras_require=extras
)
