from setuptools import setup, find_packages
from distutils.core import setup, Extension


with open("README.md", 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(
    name='ena-upload-cli',
    version='0.1.2',
    keywords=["pip", "ena-upload-cli", "cli", "ENA", "upload"],
    description='Command Line Interface to upload data to the European Nucleotide Archive',
    author="Dilmurat Yusuf",
    py_modules=['ena_upload'],
    include_package_data=True,
    author_email="bjoern.gruening@gmail.com",
    long_description_content_type='text/markdown',
    long_description=long_description,
    url="https://github.com/usegalaxy-eu/ena-upload-cli",
    packages=find_packages(),
    license='MIT',
    install_requires=[required],
    classifiers=[
        "Operating System :: OS Independent"
    ],
    python_requires='>=2.7',
    entry_points={
        "console_scripts": [
            "ena-upload-cli = ena_upload:main"
        ]
    },
)
