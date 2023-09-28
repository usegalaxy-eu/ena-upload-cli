from typing import List, Dict

from decopatch import class_decorator
from exceptiongroup import catch
from ena_objects.ena_std_lib import validate_dict


class IsaBase:
    """
    This is the base class
    """

    @classmethod
    def check_dict_keys(self, dict: Dict, mandatory_keys):
        [validate_dict(dict=dict, key=key) for key in mandatory_keys]


# class Category(IsaBase):
#     """
#     This represents a category object in a Characteristic
#     """

#     def __init__(self, id: str, name: str) -> None:
#         self.id = id
#         self.name = name

#     mandatory_keys = ["@id"]

#     @classmethod
#     def from_dict(self, dict: Dict, categories: Dict):
#         super().check_dict_keys(dict, self.mandatory_keys)

#         return self(id=dict["@id"], name=fetch_category_name(categories, dict))


# class Value(IsaBase):
#     """
#     This represents a Value object in a Characteristic
#     """

#     mandatory_keys = ["annotationValue", "termSource", "termAccession"]

#     def __init__(
#         self, annotation_value: str, term_source: str = "", term_accession: str = ""
#     ) -> None:
#         self.annotation_value = annotation_value
#         self.term_source = term_source
#         self.term_accession = term_accession

#     @classmethod
#     def from_dict(self, dict: Dict):
#         super().check_dict_keys(dict, self.mandatory_keys)

#         return Value(
#             annotation_value=dict["annotationValue"],
#             term_accession=dict["termAccession"],
#             term_source=dict["termSource"],
#         )


# class Unit(IsaBase):
#     """
#     This represents the Unit object in a Characteristic
#     """

#     mandatory_keys = ["termSource", "termAccession", "comments"]

#     def __init__(
#         self, term_source: str, term_accession: str, comments: List[str]
#     ) -> None:
#         self.term_source = term_source
#         self.term_accession = term_accession
#         self.comments = comments

#     @classmethod
#     def from_dict(self, dict: Dict):
#         super().check_dict_keys(dict, self.mandatory_keys)

#         return Unit(
#             term_source=dict["termSource"],
#             term_accession=dict["termAccession"],
#             comments=dict["comments"],
#         )


def fetch_category_name(categories: Dict, name: str) -> str:
    for cat in categories:
        if name["@id"] == cat["id"]:
            if "name" in cat:
                return cat["name"]
            elif "value" in cat:
                return cat["value"]


def category_dict(dict: Dict, categories: Dict):
    category_name = fetch_category_name(categories, dict)
    category_id = dict["@id"]
    return {"id": category_id, "name": category_name}


class Characteristic(IsaBase):
    """
    This is the base class of a characteristics object.
    """

    mandatory_keys = ["category", "value", "unit"]
    parameters = []

    def __init__(self, category: Dict, value: str) -> None:
        self.category = category
        self.value = value

    @classmethod
    def from_dict(self, dict: Dict, categories: Dict):
        super().check_dict_keys(dict, self.mandatory_keys)
        return self(
            category=category_dict(dict["category"], categories),
            value=dict["value"]["annotationValue"],
        )

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "value": self.value,
        }
