import json
from isa_objects.isa_study import IsaStudy

from rich import print_json

# Read json file
isa_json_file = open("read-isa-json/test_isa_json_files/test_local_instance.json")
isa_json = json.load(isa_json_file)

study_information = IsaStudy.from_isa_json(isa_json)
print(study_information)
