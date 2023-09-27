import os
import pytest
import json
from ena_objects.ena_study import EnaStudy, EnaSample, EnaExperiment, EnaRun

test_isa_jsonfile = open("tests/test_data/isa_json_test_investigation.json")

test_isa_json = json.load(test_isa_jsonfile)


class TestEnaStudy:
    """Test class for Ena Study objects"""

    bad_dict = {
        "title": "My Title",
        "study_description": "Should 'description'",
        "publications": None,
    }

    test_study_dict = {
        "alias": "https://datahub.elixir-belgium.org/studies/2",
        "title": "ENA Upload Study",
        "study_type": "",
        "study_abstract": "",
        "new_study_type": None,
        "pubmed_id": [1],
    }

    def test_should_raise_key_error(self):
        with pytest.raises(
            KeyError, match="description was not found in the provided ISA JSON."
        ):
            EnaStudy.from_isa_json(self.bad_dict)

    def test_ena_study_creation(self):
        studies = EnaStudy.from_isa_json(test_isa_json)

        assert len(studies) == 1
        assert studies[0].to_dict() == self.test_study_dict


class TestEnaSample:
    study_dict = test_isa_json["studies"][0]

    def test_sample_creation(self):
        samples = EnaSample.from_study_dict(self.study_dict)
        assert len(samples) == 6


class TestEnaExperiment:
    pass


class TestEnaRun:
    pass
