import json
import requests

URL = "https://www.ebi.ac.uk/ena/portal/api/search"
DEV_URL = "https://wwwdev.ebi.ac.uk/ena/portal/api/search"

def remote_check(entry_type, alias, dev):
    ''' Identidy if an ENA object is present or not '''
    query = {entry_type + '_alias': alias}
    remote_accessions = check_remote_entry(entry_type, query, dev)
    if isinstance(remote_accessions, list) and len(remote_accessions) > 0:
        print(f'\tFound: {entry_type} entry with alias {alias}')
        return True
    else:
        print(f'\tNo {entry_type} entry found with alias {alias}')
        return False


def check_remote_entry(entry_type, query_dict, dev):
    '''
    Checks if an entry with that alias exists in the ENA repos
    entry_type = [study | sample | experiment | run]
    '''
    assert entry_type in ['study', 'sample', 'experiment', 'run']
    params_dict = {}
    query_str = ' AND '.join(['%s="%s"' % (key, value) for (key, value) in query_dict.items()])
    params_dict['query'] = query_str
    params_dict['result'] = 'read_' + entry_type
    params_dict['fields'] = entry_type + '_alias'
    params_dict['format'] = 'json'
    if dev:
        response = requests.post(DEV_URL, data=params_dict)
    else:
        response = requests.post(URL, data=params_dict)
    if response.content != b'':
        return json.loads(response.content)
    return []
