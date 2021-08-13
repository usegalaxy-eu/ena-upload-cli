[![Python application](https://github.com/usegalaxy-eu/ena-upload-cli/workflows/Python%20application/badge.svg)](https://github.com/usegalaxy-eu/ena-upload-cli/actions?query=workflow%3A%22Python+application%22)
[![BioConda version](https://anaconda.org/bioconda/ena-upload-cli/badges/version.svg)](https://anaconda.org/bioconda/ena-upload-cli)
[![Pipy version](https://badge.fury.io/py/ena-upload-cli.svg)](https://pypi.org/project/ena-upload-cli/)
[![European Galaxy server](https://img.shields.io/badge/usegalaxy-.eu-brightgreen?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAASCAYAAABB7B6eAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAAsTAAALEwEAmpwYAAACC2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOlJlc29sdXRpb25Vbml0PjI8L3RpZmY6UmVzb2x1dGlvblVuaXQ+CiAgICAgICAgIDx0aWZmOkNvbXByZXNzaW9uPjE8L3RpZmY6Q29tcHJlc3Npb24+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgICAgIDx0aWZmOlBob3RvbWV0cmljSW50ZXJwcmV0YXRpb24+MjwvdGlmZjpQaG90b21ldHJpY0ludGVycHJldGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KD0UqkwAAAn9JREFUOBGlVEuLE0EQruqZiftwDz4QYT1IYM8eFkHFw/4HYX+GB3/B4l/YP+CP8OBNTwpCwFMQXAQPKtnsg5nJZpKdni6/6kzHvAYDFtRUT71f3UwAEbkLch9ogQxcBwRKMfAnM1/CBwgrbxkgPAYqlBOy1jfovlaPsEiWPROZmqmZKKzOYCJb/AbdYLso9/9B6GppBRqCrjSYYaquZq20EUKAzVpjo1FzWRDVrNay6C/HDxT92wXrAVCH3ASqq5VqEtv1WZ13Mdwf8LFyyKECNbgHHAObWhScf4Wnj9CbQpPzWYU3UFoX3qkhlG8AY2BTQt5/EA7qaEPQsgGLWied0A8VKrHAsCC1eJ6EFoUd1v6GoPOaRAtDPViUr/wPzkIFV9AaAZGtYB568VyJfijV+ZBzlVZJ3W7XHB2RESGe4opXIGzRTdjcAupOK09RA6kzr1NTrTj7V1ugM4VgPGWEw+e39CxO6JUw5XhhKihmaDacU2GiR0Ohcc4cZ+Kq3AjlEnEeRSazLs6/9b/kh4eTC+hngE3QQD7Yyclxsrf3cpxsPXn+cFdenF9aqlBXMXaDiEyfyfawBz2RqC/O9WF1ysacOpytlUSoqNrtfbS642+4D4CS9V3xb4u8P/ACI4O810efRu6KsC0QnjHJGaq4IOGUjWTo/YDZDB3xSIxcGyNlWcTucb4T3in/3IaueNrZyX0lGOrWndstOr+w21UlVFokILjJLFhPukbVY8OmwNQ3nZgNJNmKDccusSb4UIe+gtkI+9/bSLJDjqn763f5CQ5TLApmICkqwR0QnUPKZFIUnoozWcQuRbC0Km02knj0tPYx63furGs3x/iPnz83zJDVNtdP3QAAAABJRU5ErkJggg==)](https://usegalaxy.eu/root?tool_id=toolshed.g2.bx.psu.edu/repos/iuc/ena_upload/ena_upload)
[![DOI](https://zenodo.org/badge/260426680.svg)](https://zenodo.org/badge/latestdoi/260426680)


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

After a successful submission, new tsv tables will be generated with the ENA accession numbers filled in along with a submission receipt.

## Tool dependencies

* python 3.5+ including following packages:
  * Genshi
  * lxml
  * pandas
  * requests

## Installation

```
pip install ena-upload-cli
```

## Usage

```
Minimal:  ena-upoad-cli --action {add,modify,cancel,release} --center CENTER_NAME  --secret SECRET

All supported arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --action {add,modify,cancel,release}
                         add: add an object to the archive
                         modify: modify an object in the archive
                         cancel: cancel a private object and its dependent objects
                         release: release a private object immediately to public
  --study STUDY         table of STUDY object
  --sample SAMPLE       table of SAMPLE object
  --experiment EXPERIMENT
                        table of EXPERIMENT object
  --run RUN             table of RUN object
  --data [FILE [FILE ...]]
                        data for submission
  --center CENTER_NAME  specific to your Webin account
  --tool TOOL_NAME      Specify the name of the tool this submission is done with. Default: ena-upload-cli
  --tool_version TOOL_VERSION
                        Specify the version of the tool this submission is done with. Default: current version of tool
  --no_upload           Indicate if no upload should be performed and you like to submit a RUN object (e.g. if uploaded was done separately).
  --secret SECRET       .secret file containing the password of your Webin account
  -d, --dev             Flag to use the dev/sandbox endpoint of ENA.
  --vir                 Flag to use the viral sample template.
```

Mandatory arguments: --action, --center and --secret.

### ENA Webin

A Webin can be made [here](https://www.ebi.ac.uk/ena/submit/sra/#home) if you don't have one already. The *--webin_id* parameter makes use of the full username looking like: `Webin-XXXXX`. Visit [Webin online](https://www.ebi.ac.uk/ena/submit/webin) to check on your submissions or [dev Webin](https://wwwdev.ebi.ac.uk/ena/submit/webin) to check on test submissions.

### The .secret.yml file

To avoid exposing your credentials through the terminal history, it is recommended to make use of a `.secret.yml` file, containing your password and username keywords. An example is given in the root of this directory.


### Dev instance

By default the submission will be done using following url to ENA: https://www.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA

Use the *--dev* flag if you want to do a test submission using the tool by the sandbox dev instance of ENA: https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA. A TEST submission will be discarded within 24 hours.

### Supported columns for viral sample submissions

Viral samples are validated by ENA using the [ENA virus pathogen](https://www.ebi.ac.uk/ena/browser/view/ERC000033) checklist. The columns supported in the sample tsv table used by this tool are:

| Column name                          | ENA field name	                               | Field format    | Cardinality |
|--------------------------------------|-----------------------------------------------|-----------------|-------------|
| alias                                | alias                                         | free text       | mandatory   |
| status                               |                                               |                 | auto_filled |
| accession                            | accession                                     |                 | auto_filled |
| title                                | TITLE                                         | free text       | mandatory   |
| scientific_name                      | SCIENTIFIC_NAME                               | free text       | mandatory   |
| taxon_id                             | TAXON_ID                                      |                 | auto_filled |
| sample_description                   | DESCRIPTION                                   | free text       | mandatory   |
| submission_date                      |                                               |                 | auto_filled |
| geographic_location                  | geographic location (country and/or sea)      | text choice     | mandatory   |
| host_common_name                     | host common name                              | free text       | mandatory   |
| host_subject_id                      | host subject id                               | free text       | mandatory   |
| host_health_state                    | host health state                             | text choice     | mandatory   |
| host_sex                             | host sex                                      | text choice     | mandatory   |
| host_scientific_name                 | host scientific name                          | free text       | mandatory   |
| collector_name                       | collector name                                | free text       | mandatory   |
| collecting_institution               | collecting institution                        | free text       | mandatory   |
| isolate                              | isolate                                       | free text       | mandatory   |
| collection_date                      | collection date                               | restricted text | recommended |
| geographic_location_latitude         | geographic location (latitude)                | restricted text | recommended |
| geographic_location_longitude        | geographic location (longitude)               | restricted text | recommended |
| geographic_location_region           | geographic location (region and locality)     | free text       | recommended |
| sample_capture_status                | sample capture status                         | text choice     | recommended |
| host_disease_outcome                 | host disease outcome                          | text choice     | recommended |
| host_age                             | host age                                      | restricted text | recommended |
| virus_identifier                     | virus identifier                              | free text       | recommended |
| receipt_date                         | receipt date                                  | restricted text | recommended |
| definition_for_seropositive_sample   | definition for seropositive sample            | free text       | recommended |
| serotype                             | serotype (required for a seropositive sample) | free text       | recommended |
| host_habitat                         | host habitat                                  | text choice     | recommended |
| isolation_source_host_associated     | isolation source host-associated              | free text       | recommended |
| host_behaviour                       | host behaviour                                | text choice     | recommended |
| isolation_source_non_host_associated | isolation source non-host-associated          | free text       | recommended |
| subject_exposure                     | subject exposure                              | free text       | optional    |
| subject_exposure_duration            | subject exposure duration                     | free text       | optional    |
| type_exposure                        | type exposure                                 | free text       | optional    |
| personal_protective_equipment        | personal protective equipment                 | free text       | optional    |
| hospitalisation                      | hospitalisation                               | text choice     | optional    |
| illness_duration                     | illness duration                              | free text       | optional    |
| illness_symptoms                     | illness symptoms                              | free text       | optional    |
| sample_storage_conditions            | sample storage conditions                     | free text       | optional    |
| strain                               | strain                                        | free text       | optional    |
| host_description                     | host description                              | free text       | optional    |
| gravidity                            | gravidity                                     | free text       | optional    |


Please use the [ENA virus pathogen](https://www.ebi.ac.uk/ena/browser/view/ERC000033) checklist on the website of ENA to know which values are allowed/possible in the `restricted text` and `text choice` fields.


### The data files

**Supported data**

- [x] Read data
- [ ] Genome Assembly
- [ ] Transcriptome Assembly
- [x] Template Sequence
- [x] Other Analyses

Most files uploaded to the ENA FTP server need to be compressed.

More information on how ENA wants to receive the files can be found [here](https://ena-docs.readthedocs.io/en/latest/submit/fileprep/preparation.html).

**Note for data upload:** 
Uploaded files persistently stored on the ENA server after upload for some time. 
Thus, if multiple test submission are performed, it is possible to skip the data upload with `--no_upload` in
subsequent submissions.
This also allows uploading (large) datasets separately e.g. with [aspera](https://ena-docs.readthedocs.io/en/latest/submit/fileprep/upload.html).
For the `--no_upload` argument,  data file(s) still with to be provided with `--data` 
if a RUN object is submitted in order to generate MD5 sums.  


## Tool overview

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

## Test the tool

test command: **add metadata and sequence data**

 ```
 ena_upload --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev --secret .secret.yml
 ```

 test command: **modify metadata**

 ```
 ena_upload --action modify --center 'your_center_name' --study example_tables/ENA_template_studies-2020-05-01T1421.tsv --dev --secret .secret.yml
 ```

test command for **viral data**

 ```
 ena_upload --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples_vir.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev --vir --secret .secret.yml
 ```

**Note for Windows users:** Windows, by default, does not support wildcard expansion in command-line arguments.
Because of this the `--data example_data/*gz` argument should be substituted with one containing a list of the data files.
For this example, use:
```
--data example_data/ENA_TEST1.R1.fastq.gz example_data/ENA_TEST2.R1.fastq.gz example_data/ENA_TEST2.R2.fastq.gz
```
