import json
from isa_objects import isa_study

from rich import print_json

# Read json file
isa_json_file = open('test_isa_json_files/test_local_instance.json')
isa_json = json.load(isa_json_file)
# print_json(data = isa_json)

# Extracting the Study information
studies = isa_json['studies']
print_json(data=studies)

# study_information = isa_study.IsaStudy.from_isa_json(isa_json)