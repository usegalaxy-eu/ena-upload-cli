import pytest
from ena_objects.ena_study import EnaStudy


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
