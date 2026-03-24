import requests
import json
import sys

class EnaClient:
    """
    Client per interagire con le API ENA Webin REST V2 (JSON).
    """
    PRODUCTION_URL = "https://www.ebi.ac.uk/ena/submit/drop-box/submit/v2"
    DEV_URL = "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/v2"
    
    CHECKLIST_URL = "https://www.ebi.ac.uk/ena/submit/report/checklists"
    DEV_CHECKLIST_URL = "https://wwwdev.ebi.ac.uk/ena/submit/report/checklists"

    def __init__(self, webin_id, password, dev=False):
        self.webin_id = webin_id
        self.password = password
        self.dev = dev
        self.base_url = self.DEV_URL if dev else self.PRODUCTION_URL
        self.checklist_base_url = self.DEV_CHECKLIST_URL if dev else self.CHECKLIST_URL
        self.session = requests.Session()
        self.session.auth = (webin_id, password)
        self.session.trust_env = False

    def get_checklist(self, checklist_id):
        """
        Recupera la definizione di un checklist in formato JSON.
        """
        url = f"{self.checklist_base_url}/{checklist_id}"
        print(f"Fetching checklist {checklist_id} from {url}...")
        try:
            response = self.session.get(url, params={"format": "json"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching checklist {checklist_id}: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def submit_json(self, payload):
        """
        Invia la sottomissione JSON all'endpoint ENA V2.
        """
        print(f"Submitting JSON to {self.base_url}...")
        try:
            response = self.session.post(
                self.base_url,
                json=payload,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during JSON submission: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
