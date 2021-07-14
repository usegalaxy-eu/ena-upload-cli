from setuptools import setup, find_packages
import re

with open("README.md", 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

PEP440_PATTERN = r"([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?"  # noqa

with open('ena_upload/_version.py') as f:
    v = f.read().strip()
    m = re.match(r'^__version__ = "(' + PEP440_PATTERN + ')"$', v)
    if not m:
        msg = ('ena_upload/_version.py did not match pattern '
                '__version__ = "0.1.2"  (see PEP440):\n') + v
        raise Exception(msg)

setup(
    name='ena-upload-cli',
    version=m.group(1),
    keywords=["pip", "ena-upload-cli", "cli", "ENA", "upload"],
    description='Command Line Interface to upload data to the European Nucleotide Archive',
    author="Dilmurat Yusuf",
    author_email="bjoern.gruening@gmail.com",
    long_description_content_type='text/markdown',
    packages=['ena_upload'],
    package_dir={'ena_upload': 'ena_upload'},
    package_data={
        'ena_upload': ['templates/*.xml', 'templates/*.xsd']
    },
    long_description=long_description,
    url="https://github.com/usegalaxy-eu/ena-upload-cli",
    license='MIT',
    install_requires=[required],
    classifiers=[
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.5',
    entry_points={
      'console_scripts': ["ena-upload-cli=ena_upload.ena_upload:main"]
  },
)
