from typing import List, Dict
from ena_objects.ena_std_lib import validate_dict


class IsaBase:
    """
    This is the base class
    """

    def check_dict_keys(self, dict: Dict, mandatory_keys):
        [validate_dict(dict=dict, key=key) for key in mandatory_keys]


class Category(IsaBase):
    """
    This represents a category object in a Characteristic
    """

    def __init__(self, id: str) -> None:
        self.id = id

    mandatory_keys = ["id"]

    def from_dict(self, dict: Dict):
        super().check_dict_keys(dict, self.mandatory_keys)

        return Category(id=dict["id"])


class Value(IsaBase):
    """
    This represents a Value object in a Characteristic
    """

    mandatory_keys = ["annotation_value", "term_accession", "term_source"]

    def __init__(
        self, annotation_value: str, term_source: str = "", term_accession: str = ""
    ) -> None:
        self.annotation_value = annotation_value
        self.term_source = term_source
        self.term_accession = term_accession

    def from_dict(self, dict: Dict):
        super().check_dict_keys(dict, self.mandatory_keys)

        return Unit(
            annotation_value=dict["annotation_value"],
            term_accession=dict["term_accession"],
            term_source=dict["term_source"],
        )


class Unit(IsaBase):
    """
    This represents the Unit object in a Characteristic
    """

    mandatory_keys = ["tern_source", "term_accession", "comments"]

    def __init__(
        self, term_source: str, term_accession: str, comments: List[any]
    ) -> None:
        self.term_source = term_source
        self.term_accession = term_accession
        self.comments = comments

    def from_dict(self, dict: Dict):
        super().check_dict_keys(dict, self.mandatory_keys)

        return Unit(
            term_source=dict["term_source"],
            term_accession=dict["term_accession"],
            comments=dict["comments"],
        )


class Characteristic(IsaBase):
    """
    This is the base class of a characteristics object.
    """

    mandatory_keys = ["category", "value", "unit"]

    def __init__(self, category: Category, value: Value, unit: Unit) -> None:
        self.category = category
        self.value = value
        self.unit = unit

    def from_dict(self, dict: Dict):
        super().check_dict_keys(dict, self.mandatory_keys)

        return Unit(
            category=Category.from_dict(dict["category"]),
            value=Value.from_dict(dict["value"]),
            unit=Unit.from_dict(dict["unit"]),
        )
