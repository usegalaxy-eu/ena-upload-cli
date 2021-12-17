from lxml import etree
from jinja2 import Environment, FileSystemLoader
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

template_names= ["ENA.project", "SRA.common", "SRA.experiment", "SRA.run", "SRA.sample", "SRA.study", "SRA.submission"]
ENA_template_names = []

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


def main():
    for template_name in template_names:
        template_name_sm = template_name.split(".")[1]
        print(f"Downloading {template_name_sm} template")
        # Getting the xml checklist from ENA
        url = f"https://raw.githubusercontent.com/enasequence/schema/master/src/main/resources/uk/ac/ebi/ena/sra/schema/{template_name}.xsd"
        response = fetch_object(url)

        open(f'ena_upload/templates/{template_name}.xsd', 'wb').write(response)



if __name__ == "__main__":

    main()

