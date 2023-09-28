import json
from ena_objects.ena_experiment import export_experiments_to_dataframe

from ena_objects.ena_sample import export_samples_to_dataframe

from ena_objects.ena_study import EnaStudy, EnaSample, EnaExperiment

# Read json file
isa_json_file = open("tests/test_data/isa_json_test_investigation.json")
isa_json = json.load(isa_json_file)

studies = EnaStudy.from_isa_json(isa_json)
study_dfs = [study.to_dataframe() for study in studies]
print(study_dfs[0])
study = studies[0]
study_dict = isa_json["studies"][0]

samples = EnaSample.from_study_dict(study_dict)
samples_df = export_samples_to_dataframe(samples)
print(samples_df)

experiments = EnaExperiment.from_study_dict(study_dict, study.alias)
experiments_df = export_experiments_to_dataframe(experiments)
print(experiments_df)
print("Done!")
