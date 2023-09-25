from lxml import etree
from jinja2 import Environment, FileSystemLoader
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

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


def main():
    for response_object in fetching_checklists():
        checklist = response_object['accession']
        print(f"Parsing {checklist}")
        # Getting the xml checklist from ENA
        url = f"https://www.ebi.ac.uk/ena/browser/api/xml/{checklist}?download=true"
        response = fetch_object(url)

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
            units = ''
            for sub_attr in attribute:
                if sub_attr.tag == 'NAME':
                    name = sub_attr.text
                elif sub_attr.tag == 'MANDATORY':
                    cardinality = sub_attr.text
                elif sub_attr.tag == 'UNITS':
                    for unit in sub_attr:
                        units = unit.text
                    cardinality = sub_attr.text
            xml_tree[name] = {'cardinality': cardinality, 'units': units}

        # Loading the xml jinja2 template for samples
        t = env.get_template('ENA_template_samples.xml')

        # Render template with values from the ENA xml
        output_from_parsed_template = t.render(attributes=xml_tree)

        # Saving new xml template file
        with open(f"ena_upload/templates/ENA_template_samples_{checklist}.xml", "wb") as fh:
            fh.write(output_from_parsed_template.encode('utf-8'))


if __name__ == "__main__":

    main()

