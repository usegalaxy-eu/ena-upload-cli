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

## Tool dependencies

* curl
* python 2.7+ including following packages:
  * Genshi
  * lxml
  * pandas

## Installation

```
pip install ena-upload-cli
```

> Be aware that Windows can give problems with the `curl` commands executed by the script. Check that curl is available in your PATH.

## Usage

```
usage: ENA_upload [-h] --action {add,modify,cancel,release} [--study STUDY]
                  [--sample SAMPLE] [--experiment EXPERIMENT] [--run RUN]
                  [--data [FILE [FILE ...]]] --center CENTER_NAME --webin_id
                  WEBIN_ID (--password PASSWORD | --secret SECRET) [-d]


optional arguments:
  -h, --help            show this help message and exit
  --action {add,modify,cancel,release}
                         add: add an object to the archive
                         modify: modify an object in the 
  --study STUDY         table of STUDY object
  --sample SAMPLE       table of SAMPLE object
  --experiment EXPERIMENT
                        table of EXPERIMENT object
  --run RUN             table of RUN object
  --data [FILE [FILE ...]]
                        data for submission
  --center CENTER_NAME  specific to your Webin account
  --webin_id WEBIN_ID   the usermane of your Webin account
  --password PASSWORD   the password of your Webin account
  --secret SECRET       .secret file containing the password  of your Webin account
  -d, --dev             Flag to use the dev/sandbox endpoint of ENA.
```

Mandatory arguments: --action, --center, --webin_id, --password or --secret.

### ENA Webin

A Webin can be made [here](https://www.ebi.ac.uk/ena/submit/sra/#home) if you don't have one already. The *--webin_id* parameter makes use of the full username looking like: `Webin-XXXXX`. Visit [Webin online](https://www.ebi.ac.uk/ena/submit/webin) to check on your submissions or [dev Webin](https://wwwdev.ebi.ac.uk/ena/submit/webin) to check on test submissions.

### The password parameter

To avoid exposing you password through the terminal history, it is recommended to make use of a `.secret` file, containing your password on the first line. Use instead of the *--password* parameter in the ena-upload-cli tool the *--secret* parameter to specify the location of the .secret file.


### dev instance


By default the submission will be done using following url to ENA: https://www.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA

Use the *--dev* flag if you want to do a test submission using the tool by the sandbox dev instance of ENA: https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA. A TEST submission will be discarded within 24 hours

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

 `ena_upload --action add --center 'your_center_name' --webin_id your_id --password your_password --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev`

 test command: **modify a metadata**

 `ena_upload --action modify --center 'your_center_name' --webin_id your_id --password your_password --study example_tables/ENA_template_studies-2020-05-01T1421.tsv --dev`

test command **.secret file**

`ena-upload-cli --action add --center 'your_center_name' --webin_id your_id --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev --secret .secret`