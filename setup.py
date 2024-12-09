from setuptools import setup
from setuptools import find_packages
from ena_upload._version import __version__

with open("README.md", 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(
    name='ena-upload-cli',
    version=__version__,
    keywords=["pip", "ena-upload-cli", "cli", "ENA", "upload"],
    description='Command Line Interface to upload data to the European Nucleotide Archive',
    author="Dilmurat Yusuf",
    author_email="bjoern.gruening@gmail.com",
    long_description_content_type='text/markdown',
    packages= find_packages(),
    package_dir={'ena_upload': 'ena_upload'},
    package_data={
        'ena_upload': ['templates/*.xml', 'templates/*.xsd', 'json_parsing/json_schemas/*.json']
    },
    long_description=long_description,
    url="https://github.com/usegalaxy-eu/ena-upload-cli",
    license='MIT',
    install_requires=[required],
    classifiers=[
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
    entry_points={
      'console_scripts': ["ena-upload-cli=ena_upload.ena_upload:main"]
    },
)
