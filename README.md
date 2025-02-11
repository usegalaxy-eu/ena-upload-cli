[![Python application](https://github.com/usegalaxy-eu/ena-upload-cli/workflows/Python%20application/badge.svg)](https://github.com/usegalaxy-eu/ena-upload-cli/actions?query=workflow%3A%22Python+application%22)
[![BioConda version](https://anaconda.org/bioconda/ena-upload-cli/badges/version.svg)](https://anaconda.org/bioconda/ena-upload-cli)
[![Pipy version](https://badge.fury.io/py/ena-upload-cli.svg)](https://pypi.org/project/ena-upload-cli/)
[![European Galaxy server](https://img.shields.io/badge/usegalaxy-.eu-brightgreen?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAASCAYAAABB7B6eAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAAsTAAALEwEAmpwYAAACC2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOlJlc29sdXRpb25Vbml0PjI8L3RpZmY6UmVzb2x1dGlvblVuaXQ+CiAgICAgICAgIDx0aWZmOkNvbXByZXNzaW9uPjE8L3RpZmY6Q29tcHJlc3Npb24+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgICAgIDx0aWZmOlBob3RvbWV0cmljSW50ZXJwcmV0YXRpb24+MjwvdGlmZjpQaG90b21ldHJpY0ludGVycHJldGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KD0UqkwAAAn9JREFUOBGlVEuLE0EQruqZiftwDz4QYT1IYM8eFkHFw/4HYX+GB3/B4l/YP+CP8OBNTwpCwFMQXAQPKtnsg5nJZpKdni6/6kzHvAYDFtRUT71f3UwAEbkLch9ogQxcBwRKMfAnM1/CBwgrbxkgPAYqlBOy1jfovlaPsEiWPROZmqmZKKzOYCJb/AbdYLso9/9B6GppBRqCrjSYYaquZq20EUKAzVpjo1FzWRDVrNay6C/HDxT92wXrAVCH3ASqq5VqEtv1WZ13Mdwf8LFyyKECNbgHHAObWhScf4Wnj9CbQpPzWYU3UFoX3qkhlG8AY2BTQt5/EA7qaEPQsgGLWied0A8VKrHAsCC1eJ6EFoUd1v6GoPOaRAtDPViUr/wPzkIFV9AaAZGtYB568VyJfijV+ZBzlVZJ3W7XHB2RESGe4opXIGzRTdjcAupOK09RA6kzr1NTrTj7V1ugM4VgPGWEw+e39CxO6JUw5XhhKihmaDacU2GiR0Ohcc4cZ+Kq3AjlEnEeRSazLs6/9b/kh4eTC+hngE3QQD7Yyclxsrf3cpxsPXn+cFdenF9aqlBXMXaDiEyfyfawBz2RqC/O9WF1ysacOpytlUSoqNrtfbS642+4D4CS9V3xb4u8P/ACI4O810efRu6KsC0QnjHJGaq4IOGUjWTo/YDZDB3xSIxcGyNlWcTucb4T3in/3IaueNrZyX0lGOrWndstOr+w21UlVFokILjJLFhPukbVY8OmwNQ3nZgNJNmKDccusSb4UIe+gtkI+9/bSLJDjqn763f5CQ5TLApmICkqwR0QnUPKZFIUnoozWcQuRbC0Km02knj0tPYx63furGs3x/iPnz83zJDVNtdP3QAAAABJRU5ErkJggg==)](https://usegalaxy.eu/root?tool_id=toolshed.g2.bx.psu.edu/repos/iuc/ena_upload/ena_upload)
[![DOI](https://zenodo.org/badge/260426680.svg)](https://zenodo.org/badge/latestdoi/260426680)


# ENA upload tool

This command line tool (CLI) allows easy submission of experimental data and respective metadata to the European Nucleotide Archive (ENA) using tabular files or one of the excel spreadsheets that can be found on this [template repo](https://github.com/ELIXIR-Belgium/ENA-metadata-templates). The supported metadata that can be submitted includes study, sample, run and experiment info so you can use the tool for programmatic submission of everything ENA needs without the need of logging in to the Webin interface. This also includes client side validation using ENA checklists and releasing the ENA objects. This command line tool is also available as a [Galaxy tool](https://toolshed.g2.bx.psu.edu/view/iuc/ena_upload/) and can be added to you own Galaxy instance or you can make use of one of the existing Galaxy instances, like [usegalaxy.eu](https://usegalaxy.eu/root?tool_id=toolshed.g2.bx.psu.edu/repos/iuc/ena_upload/ena_upload) or [usegalaxy.be](https://usegalaxy.be/?tool_id=toolshed.g2.bx.psu.edu/repos/iuc/ena_upload/ena_upload). 

## Overview

The metadata should be provided in separate tables or files carrying similar information corresponding to the following ENA objects:

* STUDY
* SAMPLE
* EXPERIMENT
* RUN

You can set the tool to perform the following actions:

* add: add an object to the archive
* modify: modify an object in the archive
* cancel: cancel a private object and its dependent objects
* release: release a private object immediately to the public

After a successful submission, new tsv tables will be generated with the ENA accession numbers filled in along with a submission receipt.

## Tool dependencies

* python 3.8+ including following packages:
  * Genshi
  * lxml
  * pandas
  * requests
  * pyyaml
  * openpyxl
  * jsonschema


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
  --data [FILE ...]     data for submission
  --center CENTER_NAME  specific to your Webin account
  --checklist CHECKLIST
                        specify the sample checklist with following pattern: ERC0000XX, Default: ERC000011
  --xlsx XLSX           filled in excel template with metadata
  --isa_json ISA_JSON   BETA: ISA json describing describing the ENA objects
  --isa_assay_stream ISA_ASSAY_STREAM
                        BETA: specify the assay stream(s) that holds the ENA information, this can be a list of assay streams
  --auto_action         BETA: detect automatically which action (add or modify) to apply when the action column is not given
  --tool TOOL_NAME      specify the name of the tool this submission is done with. Default: ena-upload-cli
  --tool_version TOOL_VERSION
                        specify the version of the tool this submission is done with
  --no_data_upload      indicate if no upload should be performed and you like to submit a RUN object (e.g. if uploaded was done separately).
  --draft               indicate if no submission should be performed
  --secret SECRET       .secret.yml file containing the password and Webin ID of your ENA account
  -d, --dev             flag to use the dev/sandbox endpoint of ENA
```

Mandatory arguments: --action, --center and --secret.

### ENA Webin

A Webin can be made [here](https://www.ebi.ac.uk/ena/submit/sra/#home) if you don't have one already. The Webin ID makes use of the full username looking like: `Webin-XXXXX`. Visit [Webin online](https://www.ebi.ac.uk/ena/submit/webin) to check on your submissions or [dev Webin](https://wwwdev.ebi.ac.uk/ena/submit/webin) to check on test submissions.

### The .secret.yml file

To avoid exposing your credentials through the terminal history, it is recommended to make use of a `.secret.yml` file, containing your password and username keywords. An example is given in the root of this directory.

### ENA sample checklists

You can specify ENA sample checklist using the `--checklist` parameter. By default the ENA default sample checklist is used supporting the minimum information required for the sample (ERC000011). The supported checklists are listed on our [template repo](https://github.com/ELIXIR-Belgium/ENA-metadata-templates).  

#### Fixed sample columns

The command line tool will automatically fetch the correct scientific name based on the taxon ID or fetch the taxon ID based on the scientific name. Both can be given and no overwrite will be done.

- Mandatory: *alias*, *title*, *sample_description*, *collection date*,	*geographic location (country and/or sea)* and either *scientific_name* or *taxon_id* (preferred)
- Optional: *common_name*, *sample_description*

| alias          | title          | taxon_id | scientific_name                                 | common_name | sample_description   | collection date | geographic location (country and/or sea) |
|----------------|----------------|----------|-------------------------------------------------|-------------|----------------------|-----------------|------------------------------------------|
| sample_alias_4 | sample_title_2 | 2697049  | Severe acute respiratory syndrome coronavirus 2 | covid-19    | sample_description_1 | 2020-10-11      | Argentina                                |
| sample_alias_5 | sample_title_3 | 2697049  | Severe acute respiratory syndrome coronavirus 2 | covid-19    | sample_description_2 | 2008-01-24      | Belgium                                  |

#### Custom attributes

Additional custom attributes (i.e. attributes not specified in the ERC checklist) can be added to the sample table by adding columns which headers are named like `sample_attribute[attribute_name]`; for example `sample_attribute[treatment]`, `sample_attribute[age]`... An example tsv file using custom attributes can be found in [example_tables/ENA_template_samples_xtra_attrs.tsv](/example_tables/ENA_template_samples_xtra_attrs.tsv). The same syntax is also applicable for xlsx input files.

| alias          | ...            | sample_attribute[treatment] | sample_attribute[age]
|----------------|----------------|---------------------|------------------------|
| sample_alias_4 | ...            | treated             | 2 days
| sample_alias_5 | ...            | untreated           | 2 days

#### Viral submissions

If you want to submit viral samples you can use the [ENA virus pathogen](https://www.ebi.ac.uk/ena/browser/view/ERC000033) checklist by adding `ERC000033` to the checklist parameter. Check out our [viral example command](#test-the-tool) as demonstration. Please use the [ENA virus pathogen](https://github.com/ELIXIR-Belgium/ENA-metadata-templates/tree/main/templates/ERC000033) checklist in our template repo to know what is allowed/possible in the `Controlled vocabulary`fields.

### ENA study, experiment and run tables

Please check out the [template](https://github.com/ELIXIR-Belgium/ENA-metadata-templates) of your checklist to discover which attributes are mandatory for the study, experiment and run ENA object.

#### Read info run attributes

Using `read_type`	and `read_label` as header in the columns of ENA run objects will allow you to set information about reads. Values are listed in a comma separated way, without spaces. `read_type` has a controlled vocabulary, which can be found in the [ENA Documentation](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#json-manifest-file-format). An example tsv file using these attributes can be found in [example_tables/ENA_template_runs_read_info.tsv](/example_tables/ENA_template_runs_read_info.tsv). The same syntax is also applicable for xlsx input files.

#### Study and experiment custom attributes

Similarly to samples, additional custom attributes can be added to the experiment and study tables by adding columns which headers are named like `experiment_attribute[attribute_name]` and `study_attribute[attribute_name]` in the experiment and study tables, respectively.

### Dev instance

By default the submission will be done using following url to ENA: https://www.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA

Use the *--dev* flag if you want to do a test submission using the tool by the sandbox dev instance of ENA: https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA. A TEST submission will be discarded within 24 hours.

### Submitting a selection of rows to ENA

There are two ways of submitting only a selection of objects to ENA. This is handy for reoccurring submissions, especially when they belong to the same study.

- Manual: you can add an optional `status` column to every table/sheet that contains the action you want to apply during this submission. If you chose to add only the first 2 samples to ENA, you specify `--action add` as parameter in the command and you add the `add` value to the status column of the rows you want to submit as demonstrated below. Same holds for the action `modify`, `release` and `cancel`.
- Automatic (BETA): using the `--auto_action` it is possible to auto detect wether an object (using the alias) is already present on ENA and will fill in the specified action (`--action` parameter) accordingly. In practice, this means that if a user chooses to add objects and we already find this object already exists using its alias, this objects will not be added. On the other hand, if the command is used to modify objects, we want to apply this solely on objects that already exist on ENA. The detection only works with ENA objects that are published and findable on the website trough the search function (both the dev and live website). If the tool does not correctly detect the presence of your ENA object, we suggest to use the more robust manual approach as described above.

**Example with modify as seen in the [example sample modify table](example_tables/ENA_template_samples_modify.tsv)**

| alias          | status | title          | taxon_id | sample_description   |
|----------------|--------|----------------|----------|----------------------|
| sample_alias_4 | modify | sample_title_1 | 2697049  | sample_description_1 |
| sample_alias_5 |        | sample_title_2 | 2697049  | sample_description_2 |


> IMPORTANT: if the status column is given but not filled in, or filled in with a different action from the one in the `--action` parameter, no rows will be submitted! Either leave out the column or add to every row you want to submit the correct action.


### Using Excel templates

We also support the use of specific excel templates, designed for each sample checklist. Use the `--xlsx` command to add the path to an excel template file filled in from this [template repo](https://github.com/ELIXIR-Belgium/ENA-metadata-templates). 

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
For the `--no_data_upload` argument,  data file(s) still need to be provided with `--data` if a RUN object is submitted without its MD5 sums in the `file_checksum` column.

### Releasing and canceling a submission

If you want to release or cancel data, you can do so by using `cancel` or `release` in the `--action` parameter in the command line. Tables that have to be released or cancelled need an accession column with corresponding accession ids. This means that you first have to use `add` to submit your data, and use afterwords the updated table with accession ids, if you did not yet submit your data. 

By default the updated tables after submission will have the action `added` in their status column. Don't forget to change the values to `release` or `cancel` if you want to use one of these actions (or delete the status column if your action applies for the whole table).

> NOTE: Releasing a study will make all child elements like runs and experiments public.

## Tool overview

**inputs**:
* metadata tables/excelsheet/isa_json
  * examples in `example_table` and on this [template repo](https://github.com/ELIXIR-Belgium/ENA-metadata-templates) for excel sheets
  * (optional) define actions in **status** column e.g. `add`, `modify`, `cancel`, `release` (when not given the whole table is submitted)
  * to perform bulk submission of all objects, the `aliases ids` in different ENA objects should be in the association where alias ids in experiment object link all objects together
* experimental data
  * examples in `example_data`

**outputs**:
* a receipt.xml file in the working directory with the receipt from the ENA submission
* metadata tables with updated info in the same directory of inputs:
  * updated status: `added`, `modified`, `canceled`, `released`
  * accession ids
  * submission date
  * file checksums in runs table if not given
  * taxon id or scientific name in sample table if not given

## Test the tool

* **Add metadata and sequence data**
  ```
  ena-upload-cli --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev --secret .secret.yml
  ```

* **Add metadata only**
  ```
  ena-upload-cli --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs_md5sums.tsv --dev --secret .secret.yml
  ```
* **Add studies**
  ```
  ena-upload-cli --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --dev --secret .secret.yml
  ```

* **Modify sample metadata**
  ```
  ena-upload-cli --action modify --center 'your_center_name' --sample example_tables/ENA_template_samples_modify.tsv --dev --secret .secret.yml
  ```

* **Viral data**
  ```
  ena-upload-cli --action add --center 'your_center_name' --study example_tables/ENA_template_studies.tsv --sample example_tables/ENA_template_samples_vir.tsv --experiment example_tables/ENA_template_experiments.tsv --run example_tables/ENA_template_runs.tsv --data example_data/*gz --dev --checklist ERC000033 --secret .secret.yml
  ```

* **Using an Excel template**
  ```
  ena-upload-cli --action add --center 'your_center_name' --data example_data/*gz --dev --checklist ERC000033 --secret .secret.yml --xlsx example_tables/ENA_excel_example_ERC000033.xlsx 
  ```

* **Using an ISA JSON**
  ```
  ena-upload-cli --action add --center 'your_center_name' --data example_data/*gz --dev --secret .secret.yml --isa_json tests/test_data/simple_test_case_v2.json --isa_assay_stream "Ena stream 1"
  ```

* **Release submission**
  ```
  ena-upload-cli --action release --center 'your_center_name' --study example_tables/ENA_template_studies_release.tsv --dev --secret .secret.yml 
  ```

> **Note for Windows users:** Windows, by default, does not support wildcard expansion in command-line arguments.
> Because of this the `--data example_data/*gz` argument should be substituted with one containing a list of the data files.
> For this example, use:
> 
> ```
> --data example_data/ENA_TEST1.R1.fastq.gz example_data/ENA_TEST2.R1.fastq.gz example_data/ENA_TEST2.R2.fastq.gz
> ```
