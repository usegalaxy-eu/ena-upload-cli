import json
from ena_objects.ena_study import EnaStudy

# Read json file
isa_json_file = open("read-isa-json/test_isa_json_files/test_local_instance.json")
isa_json = json.load(isa_json_file)

studies = EnaStudy.from_isa_json(isa_json)
study_dfs = [study.to_dataframe() for study in studies]
print(study_dfs[0])
