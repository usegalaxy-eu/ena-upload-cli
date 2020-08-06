#! /usr/bin/env python
__authors__ = "Dilmurat Yusuf"
__copyright__ = "Copyright 2020, Dilmurat Yusuf"
__email__ = "Dilmurat.yusuf@gmail.com"
__license__ = "MIT"

import os
import sys
import subprocess
import shlex
import json
import argparse
import hashlib
import ftplib
import uuid
import datetime
from genshi.template import TemplateLoader
import pkg_resources
from lxml import etree
import pandas as pd
import tempfile


# SettingWithCopyWarning causes false positive
# e.g at df.loc[:, 'file_checksum'] = md5
pd.options.mode.chained_assignment = None


def create_dataframe(schema_tables):
    '''create pandas dataframe from the tables in schema_tables
       and return schema_dataframe

       schema_tables - a dictionary with schema:table
                       schema -- run, experiment, sample, study
                       table -- file path

       schema_dataframe - a dictionary with schema:dataframe
                          schema -- run, experiment, sample, study
                          dataframe -- pandas dataframe
    '''

    # ? would it be good to use alias to index rows?

    schema_dataframe = {}

    for schema, table in schema_tables.items():
        df = pd.read_csv(table, sep='\t', comment='#')

        # status column contain action keywords
        # for xml rendering, keywords require uppercase
        # according to scheme definition of submission
        df['status'] = df['status'].str.upper()
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
        filtered = dataframe.query('status=="{}"'.format(action))
        # ? add a function to control empty filtered, return error
        schema_targets[schema] = filtered

    return schema_targets


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
        msg = 'different file names between command line and RUN table:'
        msg = '{} {}'.format(msg, difference)
        sys.exit(msg)


def validate_xml(xsd, xml):
    '''
    validate xml against xsd scheme
    '''

    xmlschema_doc = etree.parse(source=xsd)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    doc = etree.XML(xml)

    return xmlschema.assertValid(doc)


def generate_stream(schema, targets, Template, center):
    ''' generate stream from Template cache

    :param schema: ENA objects -- run, experiment, sample, study
    :param targets: the pandas dataframe of the run targets
    :param Template: Template cache genrated by TemplateLoader
                     in genshi
    :param center: center name used to register ENA Webin

    :return: stream
    '''

    if schema == 'run':
        # These attributes are required for rendering
        # the run xml templates
        file_attrib = ['file_name', 'file_format', 'file_checksum']
        other_attrib = ['alias', 'experiment_alias']
        run_groups = targets[other_attrib].groupby(targets['alias'])
        run_groups = run_groups.experiment_alias.unique()
        file_groups = targets[file_attrib].groupby(targets['alias'])

        # param in generate() determined by the setup in template
        stream = Template.generate(run_groups=run_groups,
                                   file_groups=file_groups,
                                   center='test_cneter')
    else:
        stream = Template.generate(df=targets, center=center)

    return stream


def construct_xml(schema, stream, xsd):
    '''construct XML for ENA submission

    :param xsd: the schema definition in
                ftp://ftp.sra.ebi.ac.uk/meta/xsd/

    :return: the file name of XML for ENA submission
    '''

    xml_string = stream.render(method='xml', encoding='utf-8')

    validate_xml(xsd, xml_string)

    xml_file = os.path.join(tempfile.gettempdir(), schema + '_' + str(uuid.uuid4()) + '.xml')
    with open(xml_file, 'w') as fw:
        fw.write(xml_string.decode("utf-8") )

    print ('wrote {}'.format(xml_file))

    return xml_file


def actors(template_path):
    ''':return: the filenames of schema definitions and templates
    '''

    def add_path(dic, path):
        for schema, filename in dic.items():
            dic[schema] = '{}/{}'.format(path, filename)
        return dic

    xsds = {'run': 'SRA.run.xsd',
            'experiment': 'SRA.experiment.xsd',
            'submission': 'SRA.submission.xsd',
            'sample': 'SRA.sample.xsd',
            'study': 'SRA.study.xsd'}

    templates = {'run': 'ENA_template_runs.xml',
                 'experiment': 'ENA_template_experiments.xml',
                 'submission': 'ENA_template_submission.xml',
                 'sample': 'ENA_template_samples.xml',
                 'study': 'ENA_template_studies.xml'}

    xsds = add_path(xsds, template_path)

    return xsds, templates


def run_construct(template_path, schema_targets,  center):
    '''construct XMLs for schema in schema_targets

    :param schema_targets: dictionary of 'schema:targets' generated
                           by extract_targets()
    :param loader: object of TemplateLoader in genshi
    :param center: center name used to register ENA Webin

    :return schema_xmls: dictionary of 'schema:filename'
    '''

    xsds, templates = actors(template_path)

    schema_xmls = {}

    loader = TemplateLoader(search_path=template_path)
    for schema, targets in schema_targets.items():
        template = templates[schema]
        Template = loader.load(template)
        stream = generate_stream(schema, targets, Template, center)

        schema_xmls[schema] = construct_xml(schema, stream, xsds[schema])

    return schema_xmls


def construct_submission(template_path, action, submission_input, center):
    '''construct XML for submission

    :param action: action for submission -
    :param submission_input: schema_xmls or schema_targets depending on action
                             ADD/MODIFY: schema_xmls
                             CANCEL/RELEASE: schema_targets
    :param loader: object of TemplateLoader in genshi
    :param center: center name used to register ENA Webin

    :return submission_xml: filename of submission XML
    '''

    xsds, templates = actors(template_path)

    template = templates['submission']
    loader = TemplateLoader(search_path=template_path)
    Template = loader.load(template)

    stream = Template.generate(action=action, input=submission_input,
                               center=center)

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


def run_cmd(cmd_line):
    """Execute command line.

    :param cmd_line: the string of command line

    :return output: the string of output from execution
    """

    args = shlex.split(cmd_line)
    process = subprocess.Popen(args,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    output, stderr = process.communicate()
    return output


def get_taxon_id(scientific_name):
    """Get taxon ID for input scientific_name.

    :param scientific_name: scientific name of sample that distinguishes
                            its taxonomy
    :return taxon_id: NCBI taxonomy identifier
    """
    # endpoint for taxonomy id
    url = 'https://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name'

    # url encoding: space -> %20
    scientific_name_ = '%20'.join(scientific_name.strip().split())

    cmd_line = 'curl {}/{}'.format(url, scientific_name_)
    output = run_cmd(cmd_line).decode("utf-8") 
    try:
        taxon_id = json.loads(output)[0]['taxId']
        return taxon_id
    except ValueError:
        msg = 'Oops, no taxon ID avaible for {}. Is it a valid scientific name?'.format(scientific_name)
        sys.exit(msg)


def submit_data(file_paths, password, webin_id):
    """Submit data to webin ftp server.

    :param file_paths: a dictionary of filename string and file_path string
    :param args: the command-line arguments parsed by ArgumentParser
    """

    try:
        print ("\nconnecting to ftp.webin.ebi.ac.uk....")
        ftp = ftplib.FTP("webin.ebi.ac.uk", webin_id, password)
    except IOError:
        print (ftp.lastErrorText())
        print ("ERROR: could not connect to the ftp server.\
               Please check your login details.")

    for filename, path in file_paths.items():
        print ('uploading {}'.format(path))
        ftp.storbinary('STOR {}'.format(filename), open(path, 'rb'))
        msg = ftp.storbinary('STOR {}'.format(filename), open(path, 'rb'))
        print (msg)

    print (ftp.quit())

def columns_to_update(df):
    '''
    returns the column names where contains the cells to update
        used after processing the reciept xmls
    '''
    return df[df.apply(lambda x: x == 'to_update')].dropna(axis=1, how='all').columns


def get_cmd_line(schema_xmls, url, webin_id, password):
    '''submit compiled XML files to the given ENA server
    return the reciept object after the submission.

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


    server = '{}%20{}%20{}'.format(url, webin_id, password)
    sources = ['-F {}=@{}'.format(schema.upper(), source)
               for schema, source in schema_xmls.items()]
    sources = ' '.join(sources)

    cmd_line = 'curl -k {} {}'.format(sources, server)

    return cmd_line


def process_receipt(reciept, action):
    '''Process submission reciept from ENA.

    :param receipt: a string of XML

    :return schema_update: a dictionary - {schema:update}
                           schema: a string - 'study', 'sample',
                                              'run', 'experiment'
                           update: a dataframe with columns - 'alias',
                                   'accession', 'submission_date'
    '''
    reciept_root = etree.fromstring(reciept)

    success = reciept_root.get('success')

    if success != 'true':
        errors = []
        for element in reciept_root.findall('MESSAGES/ERROR'):
            error = element.text
            errors.append(error)
        errors = '\nOops:\n' + '\n'.join(errors)
        sys.exit(errors)

    # define expected status based on action
    status = {'ADD': 'added', 'MODIFY': 'modified',
              'CANCEL': 'cancelled', 'RELEASE': 'released'}

    def make_update(update):
        update = [(element.get('alias'), element.get('accession'),
                   receiptDate, status[action]) for element in update]
        # used for labelling dataframe
        labels = ['alias', 'accession', 'submission_date', 'status']
        df = pd.DataFrame.from_records(update, columns=labels)
        return df

    receiptDate = reciept_root.get('receiptDate')

    study_update = reciept_root.findall('STUDY')
    sample_update = reciept_root.findall('SAMPLE')
    experiment_update = reciept_root.findall('EXPERIMENT')
    run_update = reciept_root.findall('RUN')

    schema_update = {}  # schema as key, dataframe as value

    if study_update:
        schema_update['study'] = make_update(study_update)

    if sample_update:
        schema_update['sample'] = make_update(sample_update)

    if experiment_update:
        schema_update['experiment'] = make_update(experiment_update)

    if run_update:
        schema_update['run'] = make_update(run_update)

    return schema_update


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

    for schema in schema_dataframe:
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
            if schema == 'run':
                # since index is set to alias
                # then targets of run can have multiple rows with
                # identical index because each row has a file
                # which is associated with a run.
                # and a run can have multiple files.
                # the following assignment assumes 'targets' retain
                # the orginal row order in 'dataframe'
                # because targets was initially subset of 'datafram'.
                dataframe.loc[index,
                              'file_checksum'] = targets.loc[index, 'file_checksum']

    return schema_dataframe


def save_update(schema_tables_, schema_dataframe_):
    """Write updated dataframe to tsv file.

    :param schema_tables_: a dictionary - {schema:file_path}
    :param schema_dataframe_: a dictionary - {schema:dataframe}
        :schema: a string - 'study', 'sample', 'run', 'experiment'
        :file_path: a string
        :dataframe: a dataframe
    """

    print ('\nSubmission is successful:')
    for schema in schema_tables_:
        table = schema_tables_[schema]
        dataframe = schema_dataframe_[schema]

        file_name, file_extension = os.path.splitext(table)
        time = '{:%Y-%m-%dT%H%M}'.format(datetime.datetime.now())
        update_name = '{0}-{1}{2}'.format(file_name, time, file_extension)

        dataframe.to_csv(update_name, sep='\t')
        print ('save updates in {}'.format(update_name))


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

    parser = argparse.ArgumentParser(prog='ENA_upload',
                                     description='''The program makes submission
                                     of data and respective metadata to European
                                     Nucleotide Archive (ENA). The metadate
                                     should be provided in separate tables
                                     corresponding the ENA objects -- STUDY,
                                     SAMPLE, EXPERIMENT and RUN.''',
                                     formatter_class=SmartFormatter)

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
                        help='data for submission',
                        metavar='FILE')

    parser.add_argument('--center',
                        dest='center_name',
                        required=True,
                        help='specific to your Webin account')

    parser.add_argument('--webin_id',
                        required=True,
                        help='the usermane of your Webin account')

    password_group = parser.add_mutually_exclusive_group(required=True)

    password_group.add_argument('--password',
                        help='the password of your Webin account')

    password_group.add_argument('--secret',
                        help='.secret file containing the password of your Webin account')

    parser.add_argument('-d', '--dev', help="Flag to use the dev/sandbox endpoint of ENA.", action="store_true")

    args = parser.parse_args()

    # check if any table is given
    tables = set([args.study, args.sample, args.experiment, args.run])
    if tables == {None}:
        parser.error('requires at least one table for submission')

    # check if .secret file exists

    if args.secret:
        if not os.path.isfile(args.secret):
            msg = "Oops, the file {} does not exist".format(args.secret)
            parser.error(msg)


    # check if data is given when adding a 'run' table
    if args.action == 'add' and args.run is not None:
        if args.data is None:
            parser.error('Oops, requires data for submitting RUN object')

        else:
            # validate if given data is file
            for path in args.data:
                if not os.path.isfile(path):
                    msg = "Oops, the file {} does not exist".format(path)
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


def main ():
    args = process_args()
    action = args.action.upper()
    center = args.center_name
    dev = args.dev
    webin_id = args.webin_id
    password = ""

    if args.password:
        password = args.password
    else:
        secret_file = open(args.secret, "r")
        password = secret_file.readline()
        if not password:
            print( "Oops, file {} does not contain a password on the first line.".format(args.secret))
        secret_file.close()

    # ? a function needed to convert characters e.g. # -> %23 in password

    # collect the schema with table input from command-line
    schema_tables = collect_tables(args)

    # create dataframe from table
    schema_dataframe = create_dataframe(schema_tables)

    # ? add a function to sanitize characters
    # ? print 'validate table for specific action'
    # ? print 'catch error'

    # extract rows tagged by action
    # these rows are the targets for submission
    schema_targets = extract_targets(action, schema_dataframe)

    if action == 'ADD':
        # when adding run object
        # update schema_targets wit md5 hash
        # submit data
        if 'run' in schema_targets:
            # a dictionary of filename:file_path
            # ? do I have to define the absolute path
            file_paths = {os.path.basename(path): os.path.abspath(path)
                          for path in args.data}

            df = schema_targets['run']

            # check if file names identical between command line and table
            # if not, system exits
            check_filenames(file_paths, df)

            file_md5 = {filename: get_md5(path) for filename, path
                        in file_paths.items()}

            # update schema_targets wih md5 hash
            md5 = df['file_name'].apply(lambda x: file_md5[x]).values
            df.loc[:, 'file_checksum'] = md5
            schema_targets['run'] = df

            # submit data to webin ftp server
            submit_data(file_paths, password, webin_id)

        # when adding sample
        # update schema_targets with taxon ids
        if 'sample' in schema_targets:
            df = schema_targets['sample']

            # retrieve taxon id using scientific name
            print ('retrieving taxon IDs...')
            taxonID = df['scientific_name'].apply(get_taxon_id).values
            print ('taxon IDs are retrieved')
            df.loc[:, 'taxon_id'] = taxonID
            schema_targets['sample'] = df

    # ? need to add a place holder for setting up
    base_path = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.join(base_path,'templates')
    if action in ['ADD', 'MODIFY']:
        # when ADD/MODIFY,
        # requires source XMLs for 'run', 'experiment', 'sample', 'experiment'
        # schema_xmls record XMLs for all these schema and following 'submission'
        schema_xmls = run_construct(template_path, schema_targets, center)

        submission_xml = construct_submission(template_path, action,
                                              schema_xmls, center)

    elif action in ['CANCEL', 'RELEASE']:
        # when CANCEL/RELEASE, only accessions needed
        # schema_xmls only used to record the following 'submission'
        schema_xmls = {}

        submission_xml = construct_submission(template_path, action,
                                              schema_targets, center)

    schema_xmls['submission'] = submission_xml

    if dev:
        url = 'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA'
    else:
        url = 'https://www.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA'

    submit_cmd_line = get_cmd_line(schema_xmls, url, webin_id, password)

    print ('\nSubmitting XMLs to ENA server: {}'.format(url))
    receipt = run_cmd(submit_cmd_line)

    print ('\nReceipt\n')
    print (receipt)

    schema_update = process_receipt(receipt, action)

    schema_dataframe = update_table(schema_dataframe,
                                    schema_targets,
                                    schema_update)

    # save updates in new tables
    save_update(schema_tables, schema_dataframe)

    # print 'optional: need a testing script'

    # receipt example for cancel
    # <?xml version="1.0" encoding="UTF-8"?>
    # <?xml-stylesheet type="text/xsl" href="receipt.xsl"?>
    # <RECEIPT receiptDate="2017-12-05T17:07:13.874Z" submissionFile="submission_cancel.xml" success="true">
    #      <MESSAGES>
    #           <INFO>Submission has been committed.</INFO>
    #           <INFO>This submission is a TEST submission and will be discarded within 24 hours</INFO>
    #      </MESSAGES>
    #      <ACTIONS/>
    #      <ACTIONS/>
    # </RECEIPT>


if __name__ == "__main__":

    main()
