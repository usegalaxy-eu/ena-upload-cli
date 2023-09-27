import os
import pytest
import json
from ena_objects.ena_study import EnaStudy, EnaSample, EnaExperiment, EnaRun

test_isa_jsonfile = open("tests/test_data/isa_json_test_investigation.json")

test_isa_json = json.load(test_isa_jsonfile)


class TestEnaStudy:
    """Test class for Ena Study objects"""

    def test_should_raise_key_error(self):
        bad_dict = {
            "title": "My Title",
            "study_description": "Should 'description'",
            "publications": None,
        }

        with pytest.raises(
            KeyError, match="description was not found in the provided ISA JSON."
        ):
            EnaStudy.from_isa_json(bad_dict)

    def test_ena_study_creation(self):
        studies = EnaStudy.from_isa_json(test_isa_json)

        assert len(studies) == 1
        assert studies[0].__dict__() == dict(
            {
                "alias": "https://datahub.elixir-belgium.org/studies/2",
                "title": "ENA Upload Study",
                "study_type": "",
                "study_abstract": "",
                "new_study_type": None,
                "pubmed_id": [1],
            }
        )


class TestEnaSample:
    pass


class TestEnaExperiment:
    pass


class TestEnaRun:
    pass
