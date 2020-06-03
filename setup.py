from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='ena-upload-cli',
    version='0.1',
    keywords=["pip", "ena-upload", "cli"],
    description='Command Line Interface to upload data to the European Nucleotide Archive',
    author="Dilmurat Yusuf",
    author_email="bjoern.gruening@gmail.com",
    long_description_content_type='text/markdown',
    long_description=long_description,
    url="https://github.com/usegalaxy-eu/ena-upload-cli",
    packages=['.'],
    install_requires=[required],
    classifiers=[
        "Operating System :: OS Independent"
    ],
    python_requires='>=2.7',
    entry_points={
        "console_scripts": [
            "ena-upload = ena-upload:main"
        ]
    },
)
