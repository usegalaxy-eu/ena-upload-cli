from lxml import etree
from jinja2 import Environment, FileSystemLoader
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from pathlib import Path

def fetch_object(url):
    """
    Fetch single BrAPI object by path
    """
    print('  GET ' + url)
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=15)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    r = session.get(url)
    # Covering internal server errors by retrying one more time
    if r.status_code == 500:
        time.sleep(5)
        r = requests.get(url, allow_redirects=True)
    elif r.status_code != 200:
        print(f"Problem with request: {str(r)}")
        raise RuntimeError("Non-200 status code")
    return r

def fetching_checklists():
    # Gathering all checklist ID's
    session = requests.Session()
    session.trust_env = False
    response = fetch_object('https://www.ebi.ac.uk/ena/browser/api/summary/ERC000001-ERC999999')
    return response.json()['summaries']

def load_existing_units(template_path):
    """
    Load previously selected units from an existing generated XML template.
    """
    if not template_path.exists():
        return {}

    try:
        root = etree.parse(str(template_path)).getroot()
    except (OSError, etree.XMLSyntaxError):
        print(f"Could not parse existing template: {template_path}")
        return {}

    unit_map = {}
    for sample_attribute in root.iter('SAMPLE_ATTRIBUTE'):
        tag = sample_attribute.findtext('TAG')
        unit = sample_attribute.findtext('UNITS')
        if tag and unit:
            unit_map[tag] = unit
    return unit_map


def choose_unit(attribute_name, available_units, previous_units):
    """
    Keep the previously selected unit if it is still available.
    Otherwise, select the latest unit from the API-provided list.
    """
    previous_unit = previous_units.get(attribute_name)
    if previous_unit and previous_unit in available_units:
        return previous_unit

    if available_units:
        return available_units[-1]

    return ''


def main():
    is_test = False
    export_path_prefix = 'tests/' if is_test else ''

    for response_object in fetching_checklists():
        checklist = response_object['accession']
        print(f"Parsing {checklist}")
        # Getting the xml checklist from ENA
        url = f"https://www.ebi.ac.uk/ena/browser/api/xml/{checklist}?download=true"
        response = fetch_object(url)
        template_path = Path(f"{export_path_prefix}ena_upload/templates/ENA_template_samples_{checklist}.xml")
        previous_units = load_existing_units(template_path)

        # Dictionary that will contain all attributes needed
        xml_tree = {}

        # Loading templates directory
        file_loader = FileSystemLoader('ena_upload/templates/jinja_templates')
        env = Environment(loader=file_loader)

        # Parsing XML
        root = etree.fromstring(response.content)

        # Looping over all fields and storing their name and cardinality
        for attribute in root.iter('FIELD'):
            name = ''
            cardinality = ''
            units = []
            for sub_attr in attribute:
                if sub_attr.tag == 'LABEL':
                    name = sub_attr.text
                elif sub_attr.tag == 'MANDATORY':
                    cardinality = sub_attr.text
                elif sub_attr.tag == 'UNITS':
                    for unit in sub_attr:
                        if unit.text:
                            units.append(unit.text)
            chosen_unit = choose_unit(name, units, previous_units)
            xml_tree[name] = {'cardinality': cardinality, 'units': chosen_unit}

        # Loading the xml jinja2 template for samples
        t = env.get_template('ENA_template_samples.xml')

        # Render template with values from the ENA xml
        output_from_parsed_template = t.render(attributes=xml_tree)

        # Saving new xml template file

        with open(template_path, "wb") as fh:
            fh.write(output_from_parsed_template.encode('utf-8'))


if __name__ == "__main__":

    main()
