import argparse
import pathlib
import sys

import xlrd
import yaml
from check_remote import check_remote_entry
from mappings import optional_samples_cols_mapping

FILE_FORMAT = 'fastq'

# Lists of *REQUIRED* columns for each sheet/case
STUDIES_COLS = ['alias', 'title', 'study_type', 'study_abstract']
STUDIES_HEADERS = ['alias', 'status', 'accession', 'title', 'study_type',
                    'study_abstract', 'pubmed_id', 'submission_date']

SAMPLES_HEADERS = ['alias', 'title', 'scientific_name', 'sample_description', 'status',
                   'accession', 'taxon_id', 'submission_date']
SAMPLES_HEADERS_VIRAL = SAMPLES_HEADERS + ['geographic location (country and/or sea)',
                                           'host common name', 'host subject id',
                                           'host health state', 'host sex', 'host scientific name',
                                           'collector name', 'collecting institution', 'isolate']

SAMPLES_COLS_BASE = ['alias', 'title', 'scientific_name', 'sample_description']
SAMPLES_COLS_VIRAL = SAMPLES_COLS_BASE + ['geographic location (country and/or sea)',
                                          'host common name', 'host health state',
                                          'host sex', 'host scientific name', 'collector name',
                                          'collecting institution', 'isolate']

EXPERIMENTS_COLUMNS = ['alias', 'title', 'study_alias', 'sample_alias', 'design_description',
               'library_name', 'library_strategy', 'library_source', 'library_selection',
               'library_layout', 'insert_size', 'library_construction_protocol',
               'platform', 'instrument_model']
EXPERIMENTS_HEADERS = ['alias', 'status', 'accession', 'title', 'study_alias',
                       'sample_alias', 'design_description', 'library_name',
                       'library_strategy', 'library_source', 'library_selection',
                       'library_layout', 'insert_size', 'library_construction_protocol',
                       'platform', 'instrument_model', 'submission_date']

RUNS_COLUMNS = ['alias', 'experiment_alias', 'file_name', 'file_format']
RUN_TABLE_HEADERS = ['alias', 'status', 'accession', 'experiment_alias', 'file_name',
                                'file_format', 'file_checksum', 'submission_date']


def identify_action(entry_type, alias):
    ''' define action ['add' | 'modify'] that needs to be perfomed for this entry '''
    query = {entry_type + '_alias': alias}
    remote_accessions = check_remote_entry(entry_type, query)
    if isinstance(remote_accessions, list) and len(remote_accessions) > 0:
        print(f'Found: {entry_type} entry with alias {alias}')
        return 'modify'
    else:
        print(f'No {entry_type} entry found with alias {alias}')
        return 'add'


def extract_data(xl_sheet, schema_type , expected_columns, optional_cols=None):
    """
    1. Check that the columns I expect are present in the sheet
    (any order and mixed with others, it's just a verification that
    the user filled the correct template)
    2. Loads the data in the sheets in dictionaries indexed by first column:
        - A dict with the required columns (listed in expected_columns)
        - A dict with the optional columns (listed in optional_cols parameter)
    """
    if xl_sheet.nrows < 3:
        raise ValueError(f'No entries found in {schema_type} sheet')
    sheet_columns = {}
    if optional_cols is None:
        optional_cols = []
    optional_cols_loaded = []
    for sh_col in range(xl_sheet.ncols):
        if (xl_sheet.cell(0, sh_col).value in expected_columns) \
           or (xl_sheet.cell(0, sh_col).value in optional_cols):
            if xl_sheet.cell(0, sh_col).value in sheet_columns.keys():
                sys.exit("Duplicated columns found")
            else:
                sheet_columns[xl_sheet.cell(0, sh_col).value] = sh_col
                if xl_sheet.cell(0, sh_col).value in optional_cols:
                    # store the list of optional cols available
                    optional_cols_loaded.append(xl_sheet.cell(0, sh_col).value)
    provided_cols = expected_columns + optional_cols_loaded

    # check that the required columns are all present
    # TODO: revise this for optional columns
    for col in range(len(expected_columns)):
        assert expected_columns[col] in sheet_columns.keys(), \
            "Expected column %s not found" % expected_columns[col]

    # fetch rows in a dict
    data_dict = {}
    # the first of the expected columns will be the index
    index_col = sheet_columns[expected_columns[0]]
    # skip first 2 rows: column names + comments rows
    for row_id in range(2, xl_sheet.nrows):
        row_dict = {}
        for col in range(1, len(provided_cols)):
            sheet_col_index = sheet_columns[provided_cols[col]]
            row_dict[provided_cols[col]] = xl_sheet.cell(row_id, sheet_col_index).value
        # should check for duplicate alias/ids?
        if xl_sheet.cell(row_id, index_col).value in data_dict.keys():
            tmp = data_dict[xl_sheet.cell(row_id, index_col).value]
            data_dict[xl_sheet.cell(row_id, index_col).value] = [tmp]
            data_dict[xl_sheet.cell(row_id, index_col).value].append(row_dict)
        else:
            data_dict[xl_sheet.cell(row_id, index_col).value] = row_dict
    return data_dict, optional_cols_loaded


def paste_xls2yaml(xlsx_path):
    print('YAML -------------')
    xls = xlrd.open_workbook(xlsx_path)
    content_dict = {}
    for sheet_name in xls.sheet_names():
        if sheet_name == 'controlled_vocabulary':
            continue
        xls_sheet = xls.sheet_by_name(sheet_name)
        sheet_contents_dict = {}
        colnames = []
        for col in range(xls_sheet.ncols):
            colnames.append(xls_sheet.cell(0, col).value)
        # skip first 2 rows (column names and suggestions)
        for row_id in range(2, xls_sheet.nrows):
            row_dict = {}
            for col_id in range(0, xls_sheet.ncols):
                row_dict[colnames[col_id]] = xls_sheet.cell(row_id, col_id).value
            # should check for duplicate alias/ids?
            sheet_contents_dict[row_id] = row_dict
        content_dict[sheet_name] = sheet_contents_dict
    yaml.dump(content_dict, sys.stdout)
    print('YAML -------------')

def get_sample_row_values(sample_alias, sample, dev_submission, action, viral_submission):
    if dev_submission:
        entry_action = action
    else:
        entry_action = identify_action('sample', sample_alias)
    samples_row_values = [sample_alias, sample['title'], sample['scientific_name'],
                          sample['sample_description'], entry_action, 'ena_accession',
                          '', 'ENA_submission_date']
    if viral_submission:
        # add the values that are unique for the viral samples
        if sample['collector name'] == '':
            sample['collector name'] = 'unknown'
        samples_row_values = samples_row_values + \
            [sample['geographic location (country and/or sea)'], sample['host common name'],
             'host subject id', sample['host health state'], sample['host sex'],
             sample['host scientific name'], sample['collector name'],
             sample['collecting institution'], sample['isolate']]
        # add the (possible) optional columns values
        if len(samples_optional_cols_loaded) > 0:
            for optional_col in samples_optional_cols_loaded:
                # parse values stored as in excel date format (=float)
                if optional_col in ('collection date', 'receipt date'):
                    # check if excel stored it as date
                    if isinstance(sample[optional_col], float):
                        year, month, day, hour, minute, second = xlrd.xldate_as_tuple(
                            sample[optional_col], xl_workbook.datemode)
                        month = "{:02d}".format(month)
                        day = "{:02d}".format(day)
                        hour = "{:02d}".format(hour)
                        minute = "{:02d}".format(minute)
                        second = "{:02d}".format(second)
                        if optional_col in ('collection date'):
                            # collection date uses the format 2008-01-23T19:23:10
                            sample[optional_col] = str(year) + '-' + str(month) + '-' + str(day) + \
                                'T' + str(hour) + ':' + str(minute) + ':' + str(second)
                        if optional_col in ('receipt date'):
                            # receipt date uses forma: 2008-01-23
                            sample[optional_col] = str(year) + '-' + str(month) + '-' + str(day)
                # excel stores everything as float so I need to check if
                # the value was actually an int and keep it as int
                if isinstance(sample[optional_col], float):
                    if int(sample[optional_col]) == sample[optional_col]:
                        # it is not really a float but an int
                        sample[optional_col] = int(sample[optional_col])
                samples_row_values.append(str(sample[optional_col]))
    return samples_row_values

def write_headers(studies_table, samples_table, exp_table, runs_table, viral_submission, samples_optional_cols_loaded):
    studies_table.write('\t'.join(['alias', 'status', 'accession', 'title', 'study_type',
                                   'study_abstract', 'pubmed_id', 'submission_date']) + '\n')
    if viral_submission:
        # extend the samples columns with the viral specific data
        samples_headers = SAMPLES_HEADERS_VIRAL 
        if len(samples_optional_cols_loaded) > 0:
            for optional_cols_excel in samples_optional_cols_loaded:
                samples_headers.append(optional_samples_cols_mapping[optional_cols_excel])
    else:
        samples_headers = SAMPLES_HEADERS
    samples_table.write('\t'.join(samples_headers) + '\n')
    exp_table.write('\t'.join(EXPERIMENTS_HEADERS))
    runs_table.write('\t'.join(RUN_TABLE_HEADERS) + '\n')


def write_to_table_files(out_base_path, dev_submission, viral_submission, action, studies_dict, samples_dict, samples_optional_cols_loaded, experiments_dict, runs_dict):
    # WRITE HEADERS TO TABLES
    studies_table =     open(pathlib.Path(out_base_path) / 'studies.tsv', 'w')
    samples_table =     open(pathlib.Path(out_base_path) / 'samples.tsv', 'w')
    experiments_table = open(pathlib.Path(out_base_path) / 'experiments.tsv', 'w')
    runs_table =        open(pathlib.Path(out_base_path) / 'runs.tsv', 'w')
    write_headers(studies_table, samples_table, experiments_table, runs_table, viral_submission,
                  samples_optional_cols_loaded)

    # track which experiment and runs are in listed
    # just to check if they all have a matching sample
    runs_included = []
    exp_included = []
    for study_alias, study in studies_dict.items():
        # study_alias = study_alias + '_' + timestamp
        if dev_submission:
            entry_action = args.action
        else:
            entry_action = identify_action('study', study_alias)
        studies_table.write('\t'.join([study_alias, entry_action, 'ENA_accession', study['title'],
                                       study['study_type'], study['study_abstract'], '',
                                       'ENA_submission_data']) + '\n')  # assuming no pubmed_id
    for sample_alias, sample in samples_dict.items():
        samples_row_values = get_sample_row_values(sample_alias, sample, dev_submission, action,
                                                   viral_submission)
        samples_table.write('\t'.join(samples_row_values) + '\n')
        for exp_alias, exp in experiments_dict.items():
            # process the experiments for this sample
            if exp['sample_alias'] == sample_alias:
                # check the remote status
                if dev_submission:
                    entry_action = args.action
                else:
                    entry_action = identify_action('experiment', exp_alias)
                experiments_table.write('\t'.join([exp_alias, entry_action, 'accession_ena', exp['title'],
                                                   exp['study_alias'], sample_alias,
                                                   exp['design_description'], exp['library_name'],
                                                   exp['library_strategy'], exp['library_source'],
                                                   exp['library_selection'],
                                                   exp['library_layout'].lower(),
                                                   str(int(exp['insert_size'])),
                                                   exp['library_construction_protocol'],
                                                   exp['platform'], exp['instrument_model'],
                                                   'submission_date_ENA']) + '\n')
                exp_included.append(exp_alias)
                for run_alias, run in runs_dict.items():
                    # check that the experiments library_layout is set to paired
                    # when multiple entries are associated with the same run alias
                    if not isinstance(run, list):
                        runs_list = [run]
                    else:
                        runs_list = run
                    for run_entry in runs_list:
                        if run_entry['experiment_alias'] == exp_alias:
                            if dev_submission:
                                entry_action = args.action
                            else:
                                entry_action = identify_action('run', run_alias)
                            runs_table.write('\t'.join([run_alias, entry_action, 'ena_run_accession',
                                                        exp_alias, run_entry['file_name'],
                                                        FILE_FORMAT, '',
                                                        'submission_date_ENA']) + '\n')
                    runs_included.append(run_alias)

    # check if any experiment or run was not associated with any sample
    for run in runs_dict.keys():
        if run not in runs_included:
            print(f'The run {run} is listed in the runs section but not associated with any \
                  used experiment')

    for exp in experiments_dict.keys():
        if exp not in exp_included:
            print(f'The experiment {exp} is listed in the experiments section but not associated \
                  with any used sample')

    studies_table.close()
    samples_table.close()
    experiments_table.close()
    runs_table.close()


def parse_xlsx_to_pandas(xlsx_path, dev_submission, viral_submission, action):

    import pandas as pd
    xl_workbook = xlrd.open_workbook(xlsx_path)
    pandas_tables = {}  # load the parsed data in a dict: sheet_name -> pandas_frame

    # PARSE STUDIES
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_study')
    studies_dict, _ = extract_data(xl_sheet, 'studies', STUDIES_COLS)

    # PARSE SAMPLES
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_sample')
    if viral_submission:
        # load columns names from the table
        samples_dict, samples_optional_cols_loaded = extract_data(xl_sheet, 'samples', SAMPLES_COLS_VIRAL,
                                                              optional_samples_cols_mapping.keys())
    else:
        samples_dict, samples_optional_cols_loaded = extract_data(xl_sheet, 'samples', SAMPLES_COLS_BASE,
                                                              optional_samples_cols_mapping.keys())
    # PARSE EXPERIMENTS
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_experiment')
    experiments_dict, _ = extract_data(xl_sheet, 'experiments', EXPERIMENTS_COLUMNS)

    # PARSE RUNS SHEET
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_run')
    runs_dict, _ = extract_data(xl_sheet, 'runs', RUNS_COLUMNS)

    # list of rows from to build the pandas DF
    studies_list = [STUDIES_HEADERS]
    for study_alias, study in studies_dict.items():
        if dev_submission:
            entry_action = action
        else:
            entry_action = identify_action('study', study_alias)
        studies_list.append([study_alias, entry_action, 'ENA_accession', study['title'],
                                       study['study_type'], study['study_abstract'], '',
                                       'ENA_submission_data'])

    if viral_submission:
        samples_list = [SAMPLES_HEADERS_VIRAL]
    else:
        samples_list = [SAMPLES_HEADERS]
    experiments_list = [EXPERIMENTS_HEADERS]
    runs_rows_list = [RUN_TABLE_HEADERS]
    runs_included = []
    exp_included = []
    for sample_alias, sample in samples_dict.items():
        samples_row_values = get_sample_row_values(sample_alias, sample, dev_submission, action,
                                                   viral_submission)
        samples_list.append(samples_row_values)
        for exp_alias, exp in experiments_dict.items():
            # process the experiments for this sample
            if exp['sample_alias'] == sample_alias:
                # check the remote status
                if dev_submission:
                    entry_action = action
                else:
                    entry_action = identify_action('experiment', exp_alias)
                experiments_list.append([exp_alias, entry_action, 'accession_ena', exp['title'],
                                                   exp['study_alias'], sample_alias,
                                                   exp['design_description'], exp['library_name'],
                                                   exp['library_strategy'], exp['library_source'],
                                                   exp['library_selection'],
                                                   exp['library_layout'].lower(),
                                                   str(int(exp['insert_size'])),
                                                   exp['library_construction_protocol'],
                                                   exp['platform'], exp['instrument_model'],
                                                   'submission_date_ENA'])
                exp_included.append(exp_alias)
                for run_alias, run in runs_dict.items():
                    # check that the experiments library_layout is set to paired
                    # when multiple entries are associated with the same run alias
                    if not isinstance(run, list):
                        runs_list = [run]
                    else:
                        runs_list = run
                    for run_entry in runs_list:
                        if run_entry['experiment_alias'] == exp_alias:
                            if dev_submission:
                                entry_action = action
                            else:
                                entry_action = identify_action('run', run_alias)
                            runs_rows_list.append([run_alias, entry_action, 'ena_run_accession',
                                                        exp_alias, run_entry['file_name'],
                                                        FILE_FORMAT, '',
                                                        'submission_date_ENA'])
                    runs_included.append(run_alias)

    # check if any experiment or run was not associated with any sample
    for run in runs_dict.keys():
        if run not in runs_included:
            print(f'The run {run} is listed in the runs section but not associated with any \
                  used experiment')

    for exp in experiments_dict.keys():
        if exp not in exp_included:
            print(f'The experiment {exp} is listed in the experiments section but not associated \
                  with any used sample')



    # create the DataFrames from the generated lists of rows
    pandas_tables['studies'] = pd.DataFrame(studies_list)
    pandas_tables['samples'] = pd.DataFrame(samples_list)
    pandas_tables['experiments'] = pd.DataFrame(experiments_list)
    pandas_tables['runs'] = pd.DataFrame(runs_list)
    return pandas_tables

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--form', dest='xlsx_path', required=True)
    parser.add_argument('--out_dir', dest='out_path', required=True)
    parser.add_argument('--action', dest='action', required=True)
    parser.add_argument('--vir', dest='viral_submission', required=False, action='store_true')
    parser.add_argument('--dev', dest='dev_submission', required=False, action='store_true')
    parser.add_argument('--verbose', dest='verbose', required=False, action='store_true')
    args = parser.parse_args()

    xl_workbook = xlrd.open_workbook(args.xlsx_path)

    # PARSE STUDIES
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_study')
    studies_dict, _ = extract_data(xl_sheet, 'studies', STUDIES_COLS)

    # PARSE SAMPLES
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_sample')
    if args.viral_submission:
        # load columns names from the table
        samples_dict, samples_optional_cols_loaded = extract_data(xl_sheet, 'samples', SAMPLES_COLS_VIRAL,
                                                              optional_samples_cols_mapping.keys())
    else:
        samples_dict, samples_optional_cols_loaded = extract_data(xl_sheet, 'samples', SAMPLES_COLS_BASE,
                                                              optional_samples_cols_mapping.keys())
    # PARSE EXPERIMENTS
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_experiment')
    experiments_dict, _ = extract_data(xl_sheet, 'experiments', EXPERIMENTS_COLUMNS)

    # PARSE RUNS SHEET
    #################
    xl_sheet = xl_workbook.sheet_by_name('ENA_run')
    runs_dict, _ = extract_data(xl_sheet, 'runs', RUNS_COLUMNS)

    # WRITE LOADED DICTS
    write_to_table_files(args.out_path, args.dev_submission, args.viral_submission, args.action,
                         studies_dict, samples_dict, samples_optional_cols_loaded, experiments_dict, runs_dict)

    if args.verbose:
        paste_xls2yaml(args.xlsx_path)
