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
  --checklist CHECKLIST
                        specify the sample checklist with following pattern: ERC0000XX, Default: ERC000011
  --tool TOOL_NAME      specify the name of the tool this submission is done with. Default: ena-upload-cli
  --tool_version TOOL_VERSION
                        specify the version of the tool this submission is done with
  --no_data_upload           Indicate if no upload should be performed and you like to submit a RUN object (e.g. if uploaded was done separately).
  --secret SECRET       .secret.yml file containing the password and Webin ID of your ENA account
  -d, --dev             flag to use the dev/sandbox endpoint of ENA
```

Mandatory arguments: --action, --center and --secret.

### ENA Webin

A Webin can be made [here](https://www.ebi.ac.uk/ena/submit/sra/#home) if you don't have one already. The *--webin_id* parameter makes use of the full username looking like: `Webin-XXXXX`. Visit [Webin online](https://www.ebi.ac.uk/ena/submit/webin) to check on your submissions or [dev Webin](https://wwwdev.ebi.ac.uk/ena/submit/webin) to check on test submissions.

### The .secret.yml file

To avoid exposing your credentials through the terminal history, it is recommended to make use of a `.secret.yml` file, containing your password and username keywords. An example is given in the root of this directory.

### ENA sample checklists

You can specify ENA sample checklist using the `--checklist` parameter. By default the ENA default sample checklist is used supporting the minimum information required for the sample (ERC000011). The supported checklists are listed on the [ENA website](https://www.ebi.ac.uk/ena/browser/checklists). This website will also describe which Field Names you have to use in the header of your sample tsv table. The Field Names will be automatically mapped in the outputted xml if the correct `--checklist` parameter is given.

#### Fixed sample columns

The command line tool will automatically fetch the correct scientific name based on the taxon ID or fetch the taxon ID based on the scientific name. Both can be given and no overwrite will be done.

- Mandatory: *alias*, *title*, *sample_description* and either *scientific_name* or *taxon_id* (preferred)
- Optional: *common_name*

| alias          | title          | taxon_id | scientific_name                                 | common_name | sample_description   |
|----------------|----------------|----------|-------------------------------------------------|-------------|----------------------|
| sample_alias_4 | sample_title_2 | 2697049  | Severe acute respiratory syndrome coronavirus 2 | covid-19    | sample_description_1 |
| sample_alias_5 | sample_title_3 | 2697049  | Severe acute respiratory syndrome coronavirus 2 | covid-19    | sample_description_2 |

#### Viral submissions

If you want to submit viral samples you can use the [ENA virus pathogen](https://www.ebi.ac.uk/ena/browser/view/ERC000033) checklist by adding `ERC000033` to the checklist parameter. Check out our [viral example command](#test-the-tool) as demonstration. Please use the [ENA virus pathogen](https://www.ebi.ac.uk/ena/browser/view/ERC000033) checklist on the website of ENA to know which values are allowed/possible in the `restricted text` and `text choice` fields.


### Dev instance

By default the submission will be done using following url to ENA: https://www.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA

Use the *--dev* flag if you want to do a test submission using the tool by the sandbox dev instance of ENA: https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA. A TEST submission will be discarded within 24 hours.

### Submitting a selection of rows to ENA

Optionally you can add a status column that contains the action you want to apply during this submission. If you chose to add only the first 2 samples to ENA, you specify `--action add` as parameter in the command and you add the `add` value to the status column of the rows you want to submit as demonstrated below. Same holds for the action `modify`.

| alias          | status | title          | scientific_name  |
|----------------|--------|----------------|------------------|
| sample_alias_4 | add    | sample_title_1 | homo sapiens     |
| sample_alias_5 | add    | sample_title_2 | human metagenome |
| sample_alias_6 |        | sample_title_3 | homo sapiens     |


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
Uploaded files are persistently stored on the ENA server after the upload for some time. 
Thus, if multiple test submission are performed, it is possible to skip the data upload with `--no_data_upload` in
subsequent submissions.
This also allows uploading (large) datasets separately e.g. with [aspera](https://ena-docs.readthedocs.io/en/latest/submit/fileprep/upload.html).
For the `--no_data_upload` argument,  data file(s) still need to be provided with `--data` 
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

* **add metadata and sequence data**
  ```
  ena-upload-cli --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev --secret .secret.yml
  ```

* **modify metadata**
  ```
  ena-upload-cli --action modify --center 'your_center_name' --sample example_tables/ENA_template_samples_modify.tsv --dev --secret .secret.yml
  ```

* **viral data**
  ```
  ena-upload-cli --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples_vir.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev --checklist ERC000033 --secret .secret.yml
  ```

> **Note for Windows users:** Windows, by default, does not support wildcard expansion in command-line arguments.
> Because of this the `--data example_data/*gz` argument should be substituted with one containing a list of the data files.
> For this example, use:
> 
> ```
> --data example_data/ENA_TEST1.R1.fastq.gz example_data/ENA_TEST2.R1.fastq.gz example_data/ENA_TEST2.R2.fastq.gz
> ```
