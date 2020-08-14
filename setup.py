from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(
    name='ena-upload-cli',
    version='0.1.6',
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
    python_requires='>=2.7',
    entry_points={
      'console_scripts': ["ena-upload-cli=ena_upload.ena_upload:main"]
  },
)
