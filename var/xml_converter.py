from lxml import etree
from jinja2 import Environment, FileSystemLoader
import requests

# Gathering all checklist ID's
session = requests.Session()
session.trust_env = False
r = session.get('https://www.ebi.ac.uk/ena/browser/api/summary/ERC000001-ERC999999')

for response_object in r.json()['summaries']:
    checklist = response_object['accession']
    print(f"Parsing {checklist}")
    # Getting the xml checklist from ENA
    url = f"https://www.ebi.ac.uk/ena/browser/api/xml/{checklist}?download=true"
    r = requests.get(url, allow_redirects=True)

    # Dictionary that will contain all attributes needed
    xml_tree = {}

    # Loading templates directory
    file_loader = FileSystemLoader('ena_upload/templates')
    env = Environment(loader=file_loader)

    # Parsing XML
    root = etree.fromstring(r.content)

    # Looping over all fields and storing their name and cardinality
    for attribute in root.iter('FIELD'):
        name = ''
        cardinality = ''
        for sub_attr in attribute:
            if sub_attr.tag == 'NAME':
                name = sub_attr.text
            elif sub_attr.tag == 'MANDATORY':
                cardinality = sub_attr.text
        xml_tree[name] = cardinality

    # Loading the xml jinja2 template for samples
    t = env.get_template('ENA_template_samples.xml')

    # Render template with values from the ENA xml
    output_from_parsed_template = t.render(attributes=xml_tree)

    # Saving new xml template file
    with open(f"ena_upload/templates/ENA_template_samples_{checklist}.xml", "w") as fh:
        fh.write(output_from_parsed_template)

