from setuptools import setup, find_packages
setup(
    name = "emailgo",
    version = "1.0",
    packages = find_packages(),    
    install_requires=[
        "leveldb",
    ],
)