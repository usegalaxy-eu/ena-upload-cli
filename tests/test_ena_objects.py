import os
import jsonschema
import pytest
import json

from rich import print_json
from ena_objects.characteristic import IsaBase
from ena_objects.ena_submission import EnaSubmission, EnaSample
from ena_objects.ena_std_lib import fetch_assay_streams, study_publication_ids
from ena_objects.ena_study import EnaStudy

test_isa_jsonfile = open(
    "tests/test_data/multi_study_multi_assay_stream_investigation.json"
)
test_isa_json = json.load(test_isa_jsonfile)


class TestEnaSubmission:
    """Test class for Ena Submission objects"""

    def test_json_schema_validation(self):
        bad_investigation_isa_json_file = open(
            "tests/test_data/bad_investigation_isa_json.json"
        )
        bad_investigation_isa_json = json.load(bad_investigation_isa_json_file)

        with pytest.raises(jsonschema.ValidationError):
            IsaBase.validate_json(
                bad_investigation_isa_json, EnaSubmission.investigation_schema
            )


class TestEnaStudy:
    """Test class for Ena Study objects"""

    test_study_dict = {
        "alias": "https://datahub.elixir-belgium.org/studies/2",
        "title": "ENA Upload Study",
        "study_type": "",
        "study_abstract": "",
        "new_study_type": None,
        "pubmed_id": [1],
    }

    def test_ena_study_creation(self):
        studies = [study for study in test_isa_json["studies"]]
        assay_streams = []
        ena_studies = []
        assert len(studies) == 2

        for study in studies:
            pubmed_ids = study_publication_ids(study["publications"])
            print(f"Study pubmed ids: {pubmed_ids}")
            for assay_stream in fetch_assay_streams(study):
                assay_streams.append(assay_stream)
                ena_studies.append(EnaStudy.from_assay_stream(assay_stream, pubmed_ids))

        assert len(assay_streams) == 3


class TestEnaSample:
    study_dict = test_isa_json["studies"][0]

    def test_sample_creation(self):
        samples = EnaSample.from_study_dict(self.study_dict)
        assert len(samples) == 5


class TestEnaExperiment:
    pass


class TestEnaRun:
    pass
