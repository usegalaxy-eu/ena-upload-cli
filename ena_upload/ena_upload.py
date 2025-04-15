#! /usr/bin/env python
__authors__ = ["Dilmurat Yusuf", "Bert Droesbeke"]
__copyright__ = "Copyright 2020, Dilmurat Yusuf"
__maintainer__ = "Bert Droesbeke"
__email__ = "bert.droesbeke@vib.be"
__license__ = "MIT"

import os
import sys
import argparse
import yaml
import hashlib
import ftplib
import requests
import json
import uuid
import numpy as np
import re
from genshi.template import TemplateLoader
from lxml import etree
import pandas as pd
import tempfile
from ena_upload._version import __version__
from ena_upload.check_remote import remote_check
from ena_upload.json_parsing.ena_submission import EnaSubmission


SCHEMA_TYPES = ['study', 'experiment', 'run', 'sample']

STATUS_CHANGES = {'ADD': 'ADDED', 'MODIFY': 'MODIFIED',
              'CANCEL': 'CANCELLED', 'RELEASE': 'RELEASED'}

class MyFTP_TLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,
                                            server_hostname=self.host,
                                            session=self.sock.session)
            # fix reuse of ssl socket:
            # https://stackoverflow.com/a/53456626/10971151 and
            # https://stackoverflow.com/a/70830916/10971151
            def custom_unwrap():
                pass
            conn.unwrap = custom_unwrap
        return conn, size


def create_dataframe(schema_tables, action, dev, auto_action):
    '''create pandas dataframe from the tables in schema_tables
       and return schema_dataframe

       schema_tables - a dictionary with schema:table
                       schema -- run, experiment, sample, study
                       table -- file path

       schema_dataframe - a dictionary with schema:dataframe
                          schema -- run, experiment, sample, study
                          dataframe -- pandas dataframe
    '''

    schema_dataframe = {}

    for schema, table in schema_tables.items():
        # Read with string dtype for specific columns
        dtype_dict = {'scientific_name': 'str', 'file_checksum': 'str'}
        df = pd.read_csv(table, sep='\t', comment='#', dtype=dtype_dict, na_values=["NA", "Na", "na", "NaN"])
        df = df.dropna(how='all')
        df = check_columns(df, schema, action, dev, auto_action)
        schema_dataframe[schema] = df

    return schema_dataframe

def extract_targets(action, schema_dataframe):
    ''' extract targeted rows in dataframe tagged by action and
        return schema_targets

        action - ADD, MODIFY, CANCEL, RELEASE

        schema_dataframe/schema_targets - a dictionary with schema:dataframe
            schema -- run, experiment, sample, study
            dataframe -- pandas dataframe
    '''
    schema_targets = {}

    for schema, dataframe in schema_dataframe.items():
        filtered = dataframe.query(f'status=="{action}"')
        if not filtered.empty:
            schema_targets[schema] = filtered

    return schema_targets


def check_columns(df, schema, action, dev, auto_action):
    # checking for optional columns and if not present, adding them
    print(f"Check if all required columns are present in the {schema} table.")
    if schema == 'sample':
        optional_columns = ['accession', 'submission_date',
                          'status', 'scientific_name', 'taxon_id']
        # Ensure string dtype for scientific_name
        if 'scientific_name' not in df.columns:
            df['scientific_name'] = pd.Series(dtype='str')
    elif schema == 'run':
        optional_columns = ['accession',
                          'submission_date', 'status', 'file_checksum']
        # Ensure string dtype for file_checksum
        if 'file_checksum' not in df.columns:
            df['file_checksum'] = pd.Series(dtype='str')
    else:
        optional_columns = ['accession', 'submission_date', 'status']

    for header in optional_columns:
        if header not in df.columns:
            if header == 'status':
                if auto_action:
                    for index, row in df.iterrows():
                        remote_present = np.nan
                        try:
                            remote_present = remote_check(
                                schema, str(df['alias'][index]), dev)

                        except Exception as e:
                            print(e)
                            print(
                                f"Something went wrong with detecting the ENA object {df['alias'][index]} on the servers of ENA. This object will be skipped.")
                        if remote_present and action == 'MODIFY':
                            df.at[index, header] = action
                            print(
                                f"\t'{df['alias'][index]}' gets '{action}' as action in the status column")
                        elif not remote_present and action in ['ADD', 'CANCEL', 'RELEASE']:
                            df.at[index, header] = action
                            print(
                                f"\t'{df['alias'][index]}' gets '{action}' as action in the status column")
                        else:
                            df.at[index, header] = np.nan
                            print(
                                f"\t'{df['alias'][index]}' gets skipped since it is already present at ENA")

                else:
                    # status column contain action keywords
                    # for xml rendering, keywords require uppercase
                    # according to scheme definition of submission
                    df[header] = str(action).upper()
            else:
                df[header] = pd.Series(dtype='str')  # Initialize as string type
        else:
            if header == 'status':
                df[header] = df[header].str.upper()

    return df


def check_filenames(file_paths, run_df):
    """Compare data filenames from command line and from RUN table.

    :param file_paths: a dictionary of filename string and file_path string
    :param df: dataframe built from RUN table
    """

    cmd_input = file_paths.keys()
    table_input = run_df['file_name'].values

    # symmetric difference between two sets
    difference = set(cmd_input) ^ set(table_input)

    if difference:
        msg = f"different file names between command line and RUN table: {difference}"
        sys.exit(msg)


def check_file_checksum(df):
    '''Return True if 'file_checksum' series contains valid MD5 sums'''

    regex_valid_md5sum = re.compile('^[a-f0-9]{32}$')

    def _is_str_md5sum(x):
        if pd.notna(x):
            match = regex_valid_md5sum.fullmatch(x)
            if match:
                return True
        else:
            return False

    s = df.file_checksum.apply(_is_str_md5sum)

    return s.all()


def validate_xml(xsd, xml):
    '''
    validate xml against xsd scheme
    '''

    xmlschema_doc = etree.parse(source=xsd)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    doc = etree.XML(xml)

    return xmlschema.assertValid(doc)


def generate_stream(schema, targets, Template, center, tool):
    ''' generate stream from Template cache

    :param schema: ENA objects -- run, experiment, sample, study
    :param targets: the pandas dataframe of the run targets
    :param Template: Template cache genrated by TemplateLoader
                     in genshi
    :param center: center name used to register ENA Webin
    :param tool: dict of tool_name and tool_version , by default ena-upload-cli

    :return: stream
    '''

    # find all columns in targets which column header matches the pattern attribute[(.*)], extract the group
    # and return a dict[header] = group
    # eg for header run_attribute[sex] => {'run_attribute[sex]': 'sex'}
    pattern = re.compile(rf"{schema}_attribute\[(.*)\]")
    extra_attributes = {}
    for column in targets.columns:
        match = re.match(pattern, column)
        if match:
            extra_attributes[column] = match.group(1)

    if schema == 'run':
        # These attributes are required for rendering
        # the run xml templates
        # Adding backwards compatibility for file_format
        if 'file_format' in targets:
            targets.rename(columns={'file_format': 'file_type'}, inplace=True)
        file_attrib = ['file_name', 'file_type', 'file_checksum']
        if 'read_type' in targets:
            file_attrib.append('read_type')
        if 'read_label' in targets:
            file_attrib.append('read_label')
        if 'unencrypted_checksum' in targets:
            file_attrib.append('unencrypted_checksum')

        other_attrib = ['alias', 'experiment_alias']
        # Create groups with alias as index
        run_groups = targets[other_attrib].groupby('alias')['experiment_alias'].first().to_dict()
        file_groups = targets[file_attrib].groupby(targets['alias'])

        # param in generate() determined by the setup in template
        stream = Template.generate(run_groups=run_groups,
                                   file_groups=file_groups,
                                   center=center,
                                   extra_attributes=extra_attributes,
                                   tool_name=tool['tool_name'],
                                   tool_version=tool['tool_version'])
    else:
        stream = Template.generate(
            df=targets, center=center, extra_attributes=extra_attributes,
            tool_name=tool['tool_name'], tool_version=tool['tool_version']
        )

    return stream


def construct_xml(schema, stream, xsd):
    '''construct XML for ENA submission

    :param xsd: the schema definition in
                ftp://ftp.sra.ebi.ac.uk/meta/xsd/

    :return: the file name of XML for ENA submission
    '''

    xml_string = stream.render(method='xml', encoding='utf-8')

    validate_xml(xsd, xml_string)

    xml_file = os.path.join(tempfile.gettempdir(),
                            schema + '_' + str(uuid.uuid4()) + '.xml')
    with open(xml_file, 'w') as fw:
        fw.write(xml_string.decode("utf-8"))

    print(f'wrote {xml_file}')

    return xml_file


def actors(template_path, checklist):
    ''':return: the filenames of schema definitions and templates
    '''

    def add_path(dic, path):
        for schema, filename in dic.items():
            dic[schema] = f'{path}/{filename}'
        return dic

    xsds = {'run': 'SRA.run.xsd',
            'experiment': 'SRA.experiment.xsd',
            'submission': 'SRA.submission.xsd',
            'sample': 'SRA.sample.xsd',
            'study': 'SRA.study.xsd'}

    templates = {'run': 'ENA_template_runs.xml',
                 'experiment': 'ENA_template_experiments.xml',
                 'submission': 'ENA_template_submission.xml',
                 'sample': f'ENA_template_samples_{checklist}.xml',
                 'study': 'ENA_template_studies.xml'}

    xsds = add_path(xsds, template_path)

    return xsds, templates


def run_construct(template_path, schema_targets,  center, checklist, tool):
    '''construct XMLs for schema in schema_targets

    :param schema_targets: dictionary of 'schema:targets' generated
                           by extract_targets()
    :param loader: object of TemplateLoader in genshi
    :param center: center name used to register ENA Webin
    :param tool: dict of tool_name and tool_version , by default ena-upload-cli
    :param checklist: parameter to select a specific sample checklist

    :return schema_xmls: dictionary of 'schema:filename'
    '''

    xsds, templates = actors(template_path, checklist)

    schema_xmls = {}

    loader = TemplateLoader(search_path=template_path)
    for schema, targets in schema_targets.items():
        template = templates[schema]
        Template = loader.load(template)
        stream = generate_stream(schema, targets, Template, center, tool)
        print(f"Constructing XML for '{schema}' schema")
        schema_xmls[schema] = construct_xml(schema, stream, xsds[schema])

    return schema_xmls


def construct_submission(template_path, action, submission_input, center, checklist, tool):
    '''construct XML for submission

    :param action: action for submission -
    :param submission_input: schema_xmls or schema_targets depending on action
                             ADD/MODIFY: schema_xmls
                             CANCEL/RELEASE: schema_targets
    :param loader: object of TemplateLoader in genshi
    :param center: center name used to register ENA Webin
    :param tool: tool name, by default ena-upload-cli
    :param checklist: parameter to select a specific sample checklist

    :return submission_xml: filename of submission XML
    '''

    print(f"Constructing XML for submission schema")

    xsds, templates = actors(template_path, checklist)

    template = templates['submission']
    loader = TemplateLoader(search_path=template_path)
    Template = loader.load(template)

    stream = Template.generate(action=action, input=submission_input,
                               center=center, tool_name=tool['tool_name'], tool_version=tool['tool_version'])
    submission_xml = construct_xml('submission', stream, xsds['submission'])

    return submission_xml


def get_md5(filepath):
    '''calculate the MD5 hash of file

    :param filepath: file path

    :return: md5 hash
    '''

    md5sum = hashlib.md5()

    with open(filepath, "rb") as fr:
        while True:
            # the MD5 digest block
            chunk = fr.read(128)

            if not chunk:
                break

            md5sum.update(chunk)

    return md5sum.hexdigest()


def get_taxon_id(scientific_name):
    """Get taxon ID for input scientific_name.

    :param scientific_name: scientific name of sample that distinguishes
                            its taxonomy
    :return taxon_id: NCBI taxonomy identifier
    """
    # endpoint for taxonomy id
    url = 'http://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name'
    session = requests.Session()
    session.trust_env = False
    # url encoding: space -> %20
    scientific_name = '%20'.join(scientific_name.strip().split())
    r = session.get(f"{url}/{scientific_name}")
    try:
        taxon_id = r.json()[0]['taxId']
        return taxon_id
    except ValueError:
        msg = f'Oops, no taxon ID available for {scientific_name}. Is it a valid scientific name?'
        sys.exit(msg)


def get_scientific_name(taxon_id):
    """Get scientific name for input taxon_id.

    :param taxon_id: NCBI taxonomy identifier
    :return scientific_name: scientific name of sample that distinguishes its taxonomy
    """
    # endpoint for scientific name
    url = 'http://www.ebi.ac.uk/ena/taxonomy/rest/tax-id'
    session = requests.Session()
    session.trust_env = False
    r = session.get(f"{url}/{str(taxon_id).strip()}")
    try:
        taxon_id = r.json()['scientificName']
        return taxon_id
    except ValueError:
        msg = f'Oops, no scientific name available for {taxon_id}. Is it a valid taxon_id?'
        sys.exit(msg)


def submit_data(file_paths, password, webin_id):
    """Submit data to webin ftp server.

    :param file_paths: a dictionary of filename string and file_path string
    :param args: the command-line arguments parsed by ArgumentParser
    """
    ftp_host = "webin2.ebi.ac.uk"

    print("\nConnecting to ftp.webin2.ebi.ac.uk....")
    try:
        ftps = MyFTP_TLS(timeout=120)
        ftps.context.set_ciphers('HIGH:!DH:!aNULL')
        ftps.connect(ftp_host, port=21)
        ftps.auth()
        ftps.login(webin_id, password)
        ftps.prot_p()

    except IOError as ioe:
        print(ioe)
        sys.exit("ERROR: could not connect to the ftp server.\
               Please check your login details.")
    for filename, path in file_paths.items():
        print(f'uploading {path}')
        try:
            print(ftps.storbinary(f'STOR {filename}', open(path, 'rb')))
        except BaseException as err:
            print(f"ERROR: {err}")
            print("ERROR: If your connection times out at this stage, it probably is because of a firewall that is in place. FTP is used in passive mode and connection will be opened to one of the ports: 40000 and 50000.")
            raise
    print(ftps.quit())


def columns_to_update(df):
    '''
    returns the column names where contains the cells to update
        used after processing the receipt xmls
    '''
    return df[df.apply(lambda x: x == 'to_update')].dropna(axis=1, how='all').columns


def send_schemas(schema_xmls, url, webin_id, password):
    '''submit compiled XML files to the given ENA server
    return the receipt object after the submission.

    schema_xmls -- dictionary of schema and the corresponding XML file name
               e.g.  {'submission':'submission.xml',
                      'study':'study.xml',
                      'run':'run.xml',
                      'sample':'sample.xml',
                      'experiment':'experiment.xml'}

    url -- ENA servers
           test:
                https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA
           production:
                https://www.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA

    webin_id -- ENA webin ID of user
    password -- ENA password of user
    '''

    sources = [(schema.upper(), (source, open(source, 'rb')))
               for schema, source in schema_xmls.items()]
    session = requests.Session()
    session.trust_env = False
    r = session.post(f"{url}",
                     auth=(webin_id, password),
                     files=sources)
    return r


def process_receipt(receipt, action):
    '''Process submission receipt from ENA.

    :param receipt: a string of XML

    :return schema_update: a dictionary - {schema:update}
                           schema: a string - 'study', 'sample',
                                              'run', 'experiment'
                           update: a dataframe with columns - 'alias',
                                   'accession', 'submission_date'
    '''
    receipt_root = etree.fromstring(receipt)

    success = receipt_root.get('success')

    if success == 'true':
        print('Submission was done successfully')
    else:
        errors = []
        for element in receipt_root.findall('MESSAGES/ERROR'):
            error = element.text
            errors.append(error)
        errors = '\nOops:\n' + '\n'.join(errors)
        sys.exit(errors)

    def make_update(update, ena_type):
        update_list = []
        print(f"\n{ena_type.capitalize()} accession details:")
        for element in update:
            extract = (element.get('alias'), element.get(
                'accession'), receiptDate, STATUS_CHANGES[action])
            print("\t".join(extract))
            update_list.append(extract)
        # used for labelling dataframe
        labels = ['alias', 'accession', 'submission_date', 'status']
        df = pd.DataFrame.from_records(update_list, columns=labels)
        return df

    receiptDate = receipt_root.get('receiptDate')
    schema_update = {}  # schema as key, dataframe as value
    if action in ['ADD', 'MODIFY']:
        study_update = receipt_root.findall('STUDY')
        sample_update = receipt_root.findall('SAMPLE')
        experiment_update = receipt_root.findall('EXPERIMENT')
        run_update = receipt_root.findall('RUN')

        if study_update:
            schema_update['study'] = make_update(study_update, 'study')

        if sample_update:
            schema_update['sample'] = make_update(sample_update, 'sample')

        if experiment_update:
            schema_update['experiment'] = make_update(
                experiment_update, 'experiment')

        if run_update:
            schema_update['run'] = make_update(run_update, 'run')
        return schema_update

    # release does have the accession numbers that are released in the recipe
    elif action == 'RELEASE':
        receipt_info = {}
        infoblocks = receipt_root.findall('MESSAGES/INFO')
        for element in infoblocks:
            match = re.search('(.+?) accession "(.+?)"', element.text)
            if match and match.group(1) in receipt_info:
                receipt_info[match.group(1)].append(match.group(2))
            elif match and match.group(1) not in receipt_info:
                receipt_info[match.group(1)] = [match.group(2)]
        for ena_type, accessions in receipt_info.items():
            print(f"\n{ena_type.capitalize()} accession details:")
            update_list = []
            for accession in accessions:
                extract = (accession, receiptDate, STATUS_CHANGES[action])
                update_list.append(extract)
                print("\t".join(extract))


def update_table(schema_dataframe, schema_targets, schema_update):
    """Update schema_dataframe with info in schema_targets/update.

    :param schema_dataframe: a dictionary - {schema:dataframe}
    :param_targets: a dictionary - {schema:targets}
    :param schema_update: a dictionary - {schema:update}

    'schema' -- a string - 'study', 'sample','run', 'experiment'
    'dataframe' -- a pandas dataframe created from the input tables
    'targets' -- a filtered dataframe with 'action' keywords
                 contains updated columns - md5sum and taxon_id
    'update' -- a dataframe with updated columns - 'alias', 'accession',
                'submission_date'

    :return schema_dataframe: a dictionary - {schema:dataframe}
                              dataframe -- updated accession, status,
                                           submission_date,
                                           md5sum, taxon_id
    """

    for schema in schema_update.keys():
        dataframe = schema_dataframe[schema]
        targets = schema_targets[schema]
        update = schema_update[schema]

        dataframe.set_index('alias', inplace=True)
        targets.set_index('alias', inplace=True)
        update.set_index('alias', inplace=True)

        for index in update.index:
            dataframe.loc[index, 'accession'] = update.loc[index, 'accession']
            dataframe.loc[index,
                          'submission_date'] = update.loc[index, 'submission_date']
            dataframe.loc[index, 'status'] = update.loc[index, 'status']

            if schema == 'sample':
                dataframe.loc[index,
                              'taxon_id'] = targets.loc[index, 'taxon_id']
            elif schema == 'run':
                # Since index is set to alias
                # then targets of run can have multiple rows with
                # identical index because each row has a file
                # which is associated with a run
                # and a run can have multiple files.
                # The following assignment assumes 'targets' retain
                # the original row order in 'dataframe'
                # because targets was initially subset of 'dataframe'.
                dataframe.loc[index,
                              'file_checksum'] = targets.loc[index, 'file_checksum']

    return schema_dataframe


def update_table_simple(schema_dataframe, schema_targets, action):
    """Update schema_dataframe with info in schema_targets.

    :param schema_dataframe: a dictionary - {schema:dataframe}
    :param_targets: a dictionary - {schema:targets}

    'schema' -- a string - 'study', 'sample','run', 'experiment'
    'dataframe' -- a pandas dataframe created from the input tables
    'targets' -- a filtered dataframe with 'action' keywords
                 contains updated columns - md5sum and taxon_id

    :return schema_dataframe: a dictionary - {schema:dataframe}
                              dataframe -- updated status
    """

    for schema in schema_targets.keys():
        dataframe = schema_dataframe[schema]
        targets = schema_targets[schema]

        dataframe.set_index('alias', inplace=True)
        targets.set_index('alias', inplace=True)

        for index in targets.index:
            dataframe.loc[index, 'status'] = STATUS_CHANGES[action]

    return schema_dataframe


def save_update(schema_tables, schema_dataframe):
    """Write updated dataframe to tsv file.

    :param schema_tables_: a dictionary - {schema:file_path}
    :param schema_dataframe_: a dictionary - {schema:dataframe}
        :schema: a string - 'study', 'sample', 'run', 'experiment'
        :file_path: a string
        :dataframe: a dataframe
    """

    print('\nSaving updates in new tsv tables:')
    for schema in schema_tables:
        table = schema_tables[schema]
        dataframe = schema_dataframe[schema]

        file_name, file_extension = os.path.splitext(table)
        update_name = f'{file_name}_updated{file_extension}'
        dataframe.to_csv(update_name, sep='\t')
        print(f'{update_name}')


class SmartFormatter(argparse.HelpFormatter):
    '''subclass the HelpFormatter and provide a special intro
    for the options that should be handled "raw" ("R|rest of help").

    :adapted from: Anthon's code at
    https://stackoverflow.com/questions/3853722/python-argparse-how-to-insert-newline-in-the-help-text
    '''

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def process_args():
    '''parse command-line arguments
    '''

    parser = argparse.ArgumentParser(prog='ena-upoad-cli',
                                     description='''The program makes submission
                                     of data and respective metadata to European
                                     Nucleotide Archive (ENA) easy. The metadata
                                     can be provided in a xlsx spreadsheet or tsv tables.''',
                                     formatter_class=SmartFormatter)
    parser.add_argument('--version', action='version',
                        version='%(prog)s '+__version__)

    parser.add_argument('--action',
                        choices=['add', 'modify', 'cancel', 'release'],
                        required=True,
                        help='R| add: add an object to the archive\n'
                        ' modify: modify an object in the archive\n'
                        ' cancel: cancel a private object and its dependent objects\n'
                        ' release: release a private object immediately to public')

    parser.add_argument('--study',
                        help='table of STUDY object')

    parser.add_argument('--sample',
                        help='table of SAMPLE object')

    parser.add_argument('--experiment',
                        help='table of EXPERIMENT object')

    parser.add_argument('--run',
                        help='table of RUN object')

    parser.add_argument('--data',
                        nargs='*',
                        help='data for submission, this can be a list of files',
                        metavar='FILE')

    parser.add_argument('--center',
                        dest='center_name',
                        required=True,
                        help='specific to your Webin account')

    parser.add_argument('--checklist', help="specify the sample checklist with following pattern: ERC0000XX, Default: ERC000011", dest='checklist',
                        default='ERC000011')

    parser.add_argument('--xlsx',
                        help='filled in excel template with metadata')
    
    parser.add_argument('--isa_json',
                        help='BETA: ISA json describing describing the ENA objects')
    
    parser.add_argument('--isa_assay_stream',
                        nargs='*',
                        help='BETA: specify the assay stream(s) that holds the ENA information, this can be a list of assay streams')

    parser.add_argument('--auto_action',
                        action="store_true",
                        default=False,
                        help='BETA: detect automatically which action (add or modify) to apply when the action column is not given')

    parser.add_argument('--tool',
                        dest='tool_name',
                        default='ena-upload-cli',
                        help='specify the name of the tool this submission is done with. Default: ena-upload-cli')

    parser.add_argument('--tool_version',
                        dest='tool_version',
                        default=__version__,
                        help='specify the version of the tool this submission is done with')

    parser.add_argument('--no_data_upload',
                        default=False,
                        action="store_true",
                        help='indicate if no upload should be performed and you like to submit a RUN object (e.g. if uploaded was done separately).')

    parser.add_argument('--draft',
                        default=False,
                        action="store_true",
                        help='indicate if no submission should be performed')

    parser.add_argument('--secret',
                        required=True,
                        help='.secret.yml file containing the password and Webin ID of your ENA account')

    parser.add_argument(
        '-d', '--dev', help="flag to use the dev/sandbox endpoint of ENA", action="store_true")

    args = parser.parse_args()

    # check if any table is given
    tables = set([args.study, args.sample, args.experiment, args.run])
    if tables == {None} and not args.xlsx and not args.isa_json:
        parser.error('Requires at least one table for submission')

    # check if .secret file exists
    if args.secret:
        if not os.path.isfile(args.secret):
            msg = f"Oops, the file {args.secret} does not exist"
            parser.error(msg)

    # check if xlsx file exists
    if args.xlsx:
        if not os.path.isfile(args.xlsx):
            msg = f"Oops, the file {args.xlsx} does not exist"
            parser.error(msg)

    # check if ISA json file exists
    if args.isa_json:
        if not os.path.isfile(args.isa_json):
            msg = f"Oops, the file {args.isa_json} does not exist"
            parser.error(msg)
        if args.isa_assay_stream is None :
            parser.error("--isa_json requires --isa_assay_stream")

    # check if data is given when adding a 'run' table
    if (not args.no_data_upload and args.run and args.action.upper() not in ['RELEASE', 'CANCEL']) or (not args.no_data_upload and args.xlsx and args.action.upper() not in ['RELEASE', 'CANCEL']):
        if args.data is None:
            parser.error('Oops, requires data for submitting RUN object')

        else:
            # validate if given data is file
            for path in args.data:
                if not os.path.isfile(path):
                    msg = f"Oops, the file {path} does not exist"
                    parser.error(msg)

    return args


def collect_tables(args):
    '''collect the schema whose table is not None

    :param args: the command-line arguments parsed by ArgumentParser
    :return schema_tables: a dictionary of schema string and file path string
    '''

    schema_tables = {'study': args.study, 'sample': args.sample,
                     'experiment': args.experiment, 'run': args.run}

    schema_tables = {schema: table for schema, table in schema_tables.items()
                     if table is not None}

    return schema_tables


def update_date(date):
    if pd.isnull(date) or isinstance(date, str):
        return date
    try:
        return date.strftime('%Y-%m-%d')
    except AttributeError:
        return date
    except Exception:
        raise


def main():
    args = process_args()
    action = args.action.upper()
    center = args.center_name
    tool = {'tool_name': args.tool_name, 'tool_version': args.tool_version}
    dev = args.dev
    checklist = args.checklist
    secret = args.secret
    draft = args.draft
    xlsx = args.xlsx
    isa_json_file = args.isa_json
    isa_assay_stream = args.isa_assay_stream
    auto_action = args.auto_action

    with open(secret, 'r') as secret_file:
        credentials = yaml.load(secret_file, Loader=yaml.FullLoader)

    password = credentials['password'].strip()
    webin_id = credentials['username'].strip()

    if not password or not webin_id:
        print(
            f"Oops, file {args.secret} does not contain a password or username")
    secret_file.close()

    if xlsx:
        # create dataframe from xlsx table
        xl_workbook = pd.ExcelFile(xlsx)
        schema_dataframe = {}  # load the parsed data in a dict: sheet_name -> pandas_frame
        schema_tables = {}

        for schema in SCHEMA_TYPES:
            if schema in xl_workbook.book.sheetnames:
                xl_sheet = xl_workbook.parse(schema, header=0, na_values=["NA", "Na", "na", "NaN"])
            elif f"ENA_{schema}" in xl_workbook.book.sheetnames:
                xl_sheet = xl_workbook.parse(f"ENA_{schema}", header=0, na_values=["NA", "Na", "na", "NaN"])
            else:
                sys.exit(
                    f"The sheet '{schema}' is not present in the excel sheet {xlsx}")
            xl_sheet = xl_sheet.drop(0).dropna(how='all')
            for column_name in list(xl_sheet.columns.values):
                if 'date' in column_name:
                    xl_sheet[column_name] = xl_sheet[column_name].apply(
                        update_date)

            if True in xl_sheet.columns.duplicated():
                sys.exit("Duplicated columns found")

            xl_sheet = check_columns(
                xl_sheet, schema, action, dev, auto_action)
            schema_dataframe[schema] = xl_sheet
            path = os.path.dirname(os.path.abspath(xlsx))
            schema_tables[schema] = f"{path}/ENA_template_{schema}.tsv"
    elif isa_json_file:
        # Read json file
        with open(isa_json_file, 'r') as json_file:
            isa_json = json.load(json_file)

        schema_tables = {}
        schema_dataframe = {}
        required_assays = []
        for stream in isa_assay_stream:
            required_assays.append({"assay_stream": stream})
        submission = EnaSubmission.from_isa_json(isa_json, required_assays)
        submission_dataframes = submission.generate_dataframes()
        for schema, df in submission_dataframes.items():
            schema_dataframe[schema] = check_columns(
                df, schema, action, dev, auto_action)
            path = os.path.dirname(os.path.abspath(isa_json_file))
            schema_tables[schema] = f"{path}/ENA_template_{schema}.tsv"


    else:
        # collect the schema with table input from command-line
        schema_tables = collect_tables(args)

        # create dataframe from table
        schema_dataframe = create_dataframe(
            schema_tables, action, dev, auto_action)

    # ? add a function to sanitize characters
    # ? print 'validate table for specific action'
    # ? print 'catch error'

    # extract rows tagged by action
    # these rows are the targets for submission
    schema_targets = extract_targets(action, schema_dataframe)

    if not schema_targets:
        sys.exit(
            f"There is no table submitted having at least one row with {action} as action in the status column.")

    if action == 'ADD':
        # when adding run object
        # update schema_targets wit md5 hash
        # submit data
        if 'run' in schema_targets:
            # a dictionary of filename:file_path
            df = schema_targets['run']
            file_paths = {}
            if args.data:
                for path in args.data:
                    file_paths[os.path.basename(path)] = os.path.abspath(path)
                # check if file names identical between command line and table
                # if not, system exits
                check_filenames(file_paths, df)

            # generate MD5 sum if not supplied in table
            if file_paths and not check_file_checksum(df):
                print("No valid checksums found, generate now...", end=" ")
                file_md5 = {filename: get_md5(path) for filename, path
                            in file_paths.items()}

                # update schema_targets wih md5 hash
                md5 = df['file_name'].apply(lambda x: file_md5[x]).values
                # SettingWithCopyWarning causes false positive
                # e.g at df.loc[:, 'file_checksum'] = md5
                pd.options.mode.chained_assignment = None
                df.loc[:, 'file_checksum'] = md5
                print("done.")
            elif check_file_checksum(df):
                print("Valid checksums found", end=" ")
            else:
                sys.exit("No valid checksums found and no files given to generate checksum from. Please list the files using the --data option or specify the checksums in the run-table when the data is uploaded separately.")

            schema_targets['run'] = df

            # submit data to webin ftp server
            if args.no_data_upload:
                print(
                    "No files will be uploaded, remove `--no_data_upload' argument to perform upload.")
            elif draft:
                print(
                    "No files will be uploaded, remove `--draft' argument to perform upload.")
            else:
                submit_data(file_paths, password, webin_id)

        # when adding sample
        # update schema_targets with taxon ids or scientific names
        if 'sample' in schema_targets:
            df = schema_targets['sample']
            print('Retrieving taxon IDs and scientific names if needed')
            for index, row in df.iterrows():
                if pd.notna(row['scientific_name']) and pd.isna(row['taxon_id']):
                    # retrieve taxon id using scientific name
                    taxonID = get_taxon_id(row['scientific_name'])
                    df.loc[index, 'taxon_id'] = int(taxonID)
                elif pd.notna(row['taxon_id']) and pd.isna(row['scientific_name']):
                    # retrieve scientific name using taxon id
                    scientificName = get_scientific_name(row['taxon_id'])
                    df.loc[index, 'scientific_name'] = scientificName
                elif pd.isna(row['taxon_id']) and pd.isna(row['scientific_name']):
                    sys.exit(
                        f"No taxon_id or scientific_name was given with sample {row['alias']}.")
            print('Taxon IDs and scientific names are retrieved')
            schema_targets['sample'] = df

    # ? need to add a place holder for setting up
    base_path = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.join(base_path, 'templates')
    if action in ['ADD', 'MODIFY']:
        # when ADD/MODIFY,
        # requires source XMLs for 'run', 'experiment', 'sample', 'experiment'
        # schema_xmls record XMLs for all these schema and following 'submission'
        schema_xmls = run_construct(
            template_path, schema_targets, center, checklist, tool)

        submission_xml = construct_submission(template_path, action,
                                              schema_xmls, center, checklist, tool)

    elif action in ['CANCEL', 'RELEASE']:
        # when CANCEL/RELEASE, only accessions needed
        # schema_xmls only used to record the following 'submission'
        schema_xmls = {}

        submission_xml = construct_submission(template_path, action,
                                              schema_targets, center, checklist, tool)

    else:
        print(f"The action {action} is not supported.")
    schema_xmls['submission'] = submission_xml

    if draft:
        print("No submission will be performed, remove `--draft' argument to perform submission.")
    else:
        if dev:
            url = 'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/'
        else:
            url = 'https://www.ebi.ac.uk/ena/submit/drop-box/submit/'

        print(f'\nSubmitting XMLs to ENA server: {url}')
        receipt = send_schemas(schema_xmls, url, webin_id, password).text
        print("Printing receipt to ./receipt.xml")
        with open('receipt.xml', 'w') as fw:
            fw.write(receipt)
        try:
            schema_update = process_receipt(receipt.encode("utf-8"), action)
        except ValueError:
            print("There was an ERROR during submission:")
            sys.exit(receipt)

    if action in ['ADD', 'MODIFY'] and not draft:
        schema_dataframe = update_table(schema_dataframe,
                                            schema_targets,
                                            schema_update)
    else:
        schema_dataframe = update_table_simple(schema_dataframe,
                                               schema_targets,
                                               action)
    # save updates in new tables
    save_update(schema_tables, schema_dataframe)


if __name__ == "__main__":
    main()
