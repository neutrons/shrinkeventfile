import versioneer
from setuptools import setup, find_packages

setup(
    name="shrinkeventfile",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
)
