import json

from ena_objects.ena_sample import EnaSample, export_samples_to_dataframe

from ena_objects.ena_study import EnaStudy

# Read json file
isa_json_file = open(
    "read-isa-json/test_isa_json_files/isa_json_test_investigation.json"
)
isa_json = json.load(isa_json_file)

studies = EnaStudy.from_isa_json(isa_json)
study_dfs = [study.to_dataframe() for study in studies]
print(study_dfs[0])

study_dict = isa_json["studies"][0]

samples = EnaSample.from_study_dict(study_dict)
samples_df = export_samples_to_dataframe(samples)
print(samples_df)
print("Done!")
