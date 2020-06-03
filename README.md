# ENA upload tool

## About

The program submits experimental data and respective metadata to the European Nucleotide Archive (ENA). The metadata should be provided in separate tables corresponding to the following ENA objects:

* STUDY
* SAMPLE
* EXPERIMENT
* RUN

The program to perform the following actions:

* add: add an object to the archive
* modify: modify an object in the archive
* cancel: cancel a private object and its dependent objects (**under development**)
* release: release a private object immediately to the public (**under development**)

## The tool dependencies in LINUX

* curl
* Genshi
* subprocess
* shlex
* json
* argparse
* hashlib
* ftplib
* uuid
* datetime
* lxml
* pandas

## Installation

**Linux/macOS:**
```
sudo python3 -m pip install git+git://github.com/BackofenLab/ENA-upload-tool.git
```

**Windows:**
```
pip install git+git://github.com/BackofenLab/ENA-upload-tool.git
```

## Test the tool

**This is still a developmental version, please run the tool in the program directory for now.**

inputs:
* metadata tables
  * examples in `example_table`
  * Please define actions in **status** column e.g. `add`, `modify`, cancel, release
  * to perform bulk submission of all objects, the `aliases ids` in different ENA objects should be in the association where alias ids in experiment object link all objects together
* experimental data
  * examples in `example_data`

outputs:
* In the same directory of inputs
* metadata tables with updated info in `status` and other relevant columns, e.g:
  * updated status: `added`, `modified`, canceled, released
  * accession ids
  * submission date

test command: **add metadata and sequence data**

 `python ENA_upload.py --action add --center 'your_center_name' --webin_id your_id --password your_password --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz`

 test command: **modify a metadata**

 `python ENA_upload.py --action modify --center 'your_center_name' --webin_id your_id --password your_password --study example_tables/ENA_template_studies-2020-05-01T14\:21.tsv`
