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
    return r.content

def elem2dict(node):
    """
    Convert an lxml.etree node tree into a dict.
    """
    result = {}

    for element in node.iterchildren():
        # Remove namespace prefix
        
        key = element.tag.split('}')[1] if '}' in element.tag else element.tag
        if element.attrib and 'name' in element.attrib:
            key= element.attrib['name']
        # Process element as tree element if the inner XML contains non-whitespace content
        if element.attrib and 'value' in element.attrib:
            value = element.attrib['value']
        elif element.text and element.text.strip():
            value = element.text.strip().rstrip()
        elif element.attrib and 'type' in element.attrib:
            value = element.attrib['type']
        else:
            value = elem2dict(element)
        if key in result:
            if type(result[key]) is list:
                result[key].append(value)
            else:
                if type(result[key]) is dict:
                    tempvalue = result[key].copy
                else:
                    tempvalue = result[key]
                result[key] = [tempvalue, value]
        else:
            result[key] = value
    return result


def findkeys(node, query):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, query):
               yield x
    elif isinstance(node, dict):
        if query in node:
            yield node[query]
        for j in node.values():
            for x in findkeys(j, query):
                yield x
    
def main():
    mapping = { "run":["FILE"], "experiment":["LIBRARY_SELECTION", "LIBRARY_SOURCE", "LIBRARY_STRATEGY"], "common":["PLATFORM"]}
    template_names= ["ENA.project", "SRA.common", "SRA.experiment", "SRA.run", "SRA.sample", "SRA.study", "SRA.submission"]
    
    for template_name in template_names:
        template_name_sm = template_name.split(".")[1]
        print(f"Downloading {template_name_sm} template")
        # Getting the xml checklist from ENA
        url = f"https://raw.githubusercontent.com/enasequence/schema/master/src/main/resources/uk/ac/ebi/ena/sra/schema/{template_name}.xsd"
        response = fetch_object(url)

        open(f'ena_upload/templates/{template_name}.xsd', 'wb').write(response)
    
        if template_name_sm in mapping.keys():

            for template_block in mapping[template_name_sm]:
                # Loading templates directory
                file_loader = FileSystemLoader('ena_upload/templates/jinja_templates')
                env = Environment(loader=file_loader)

                # Parsing XSD
                parser = etree.XMLParser(recover=True, encoding='utf-8',remove_comments=True, remove_blank_text=True)
                root = etree.fromstring(response, parser)
                incl = etree.XInclude()
                incl(root)

                xsd_dict = elem2dict(root)
                if template_block == "FILE":
                    query_dict = (list(findkeys(xsd_dict, 'filetype')))[0]
                    xml_tree = query_dict['simpleType']['restriction']['enumeration']
                elif template_block == "LIBRARY_SELECTION":
                    query_dict = (list(findkeys(xsd_dict, 'typeLibrarySelection')))[0]
                    xml_tree = query_dict['restriction']['enumeration']
                elif template_block == "LIBRARY_SOURCE":
                    query_dict = (list(findkeys(xsd_dict, 'typeLibrarySource')))[0]
                    xml_tree = query_dict['restriction']['enumeration']
                elif template_block == "LIBRARY_STRATEGY":
                    query_dict = (list(findkeys(xsd_dict, 'typeLibraryStrategy')))[0]
                    xml_tree = query_dict['restriction']['enumeration']
                elif template_block == "PLATFORM":
                    platformtype_dict = (list(findkeys(xsd_dict, 'PlatformType')))[0]
                    xml_tree = {}
                    for platformtype, instrument_models in platformtype_dict['choice'].items():
                        instrument_models_dict = (list(findkeys(xsd_dict, instrument_models['complexType']['sequence']['INSTRUMENT_MODEL'].strip('com:'))))[0]
                        xml_tree[platformtype] = instrument_models_dict['restriction']['enumeration']

                else:
                    break
                
                
                print(f"Parsed values: {xml_tree}")

                # Loading the xml jinja2 template for samples
                t = env.get_template(f'ENA_template_{template_block}.xml')

                # Render template with values from the ENA xml
                output_from_parsed_template = t.render(attributes=xml_tree)

                # Saving new xml template file
                with open(f"ena_upload/templates/ENA_template_{template_block}.xml", "w") as fh:
                    fh.write(output_from_parsed_template)



if __name__ == "__main__":

    main()

