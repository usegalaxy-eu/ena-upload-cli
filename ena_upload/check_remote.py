import json
import requests

URL = "https://www.ebi.ac.uk/ena/portal/api/search"

def identify_action(entry_type, alias):
    ''' define action ['add' | 'modify'] that needs to be performed for this entry '''
    query = {entry_type + '_alias': alias}
    remote_accessions = check_remote_entry(entry_type, query)
    if isinstance(remote_accessions, list) and len(remote_accessions) > 0:
        print(f'Found: {entry_type} entry with alias {alias}')
        return 'modify'
    else:
        print(f'No {entry_type} entry found with alias {alias}')
        return 'add'


def check_remote_entry(entry_type, query_dict, out_format='json'):
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
    params_dict['format'] = out_format
    response = requests.post(URL, data=params_dict)
    if response.content != b'':
        return json.loads(response.content)
    return []
