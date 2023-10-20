import json
import os
from typing import List, Dict
import jsonschema


class IsaBase:
    """
    This is the base class
    """

    @classmethod
    def validate_json(self, isa_json: Dict[str, str], schema):
        schema_path = os.path.join(os.curdir, "ena_upload", "json_parsing", "json_schemas", schema)

        json_file = open(schema_path)
        json_schema = json.load(json_file)

        jsonschema.validate(
            isa_json,
            json_schema,
        )


def fetch_category_name(categories: Dict[str, str], name: str) -> str:
    for cat in categories:
        if name["@id"] == cat["id"]:
            if "name" in cat:
                return cat["name"]
            elif "value" in cat:
                return cat["value"]


def category_dict(dict: Dict[str, str], categories: Dict[str, str]) -> Dict[str, str]:
    """Matches the category ID to a category name and returns a dictionary of the category.

    Args:
        dict (Dict[str, str]): category dictionary
        categories (Dict[str, str]): Dictionary of the characteristics to match

    Returns:
        Dict[str, str]: Modified category dictionary
    """
    category_name = fetch_category_name(categories, dict)
    category_id = dict["@id"]
    return {"id": category_id, "name": category_name}


class Characteristic(IsaBase):
    """
    This is the generic base class of a characteristics object.
    """

    parameters = []

    def __init__(self, category: Dict, value: str) -> None:
        self.category = category
        self.value = value

    @classmethod
    def from_dict(self, dict: Dict[str, str], categories: List[Dict[str, str]]) -> None:
        """Creates a characteristic object from a dictionary

        Args:
            dict (Dict[str, str]): Characteristics dictionary
            categories (List[Dict[str, str]]): List of all characteristics categories

        Returns:
            Characteristic: _description_
        """
        return self(
            category=category_dict(dict["category"], categories),
            value=dict["value"]["annotationValue"],
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "category": self.category,
            "value": self.value,
        }


class OtherMaterialCharacteristic(Characteristic):
    """
    This class represents a Characteristic for the other material object.
    """

    def __init__(self, category: Dict, value: str) -> None:
        super().__init__(category, value)

    @classmethod
    def from_dict(
        cls, dict: Dict[str, str], characteristics_categories: Dict[str, str]
    ):
        return super().from_dict(dict, characteristics_categories)

    def to_dict(self) -> Dict[str, str]:
        return super().to_dict()


class ParameterValue(Characteristic):
    """
    This class represents a paramenter value in the isa study
    and extends the Characteristic class.
    """

    def __init__(self, category: Dict[str, str], value: str) -> None:
        super().__init__(category, value)

    @classmethod
    def from_dict(self, dict: Dict[str, str], parameters: Dict[str, str]):
        return super().from_dict(dict, parameters)

    def to_dict(self) -> Dict[str, str]:
        return super().to_dict()


class SampleCharacteristic(Characteristic):
    """
    This class represents a Sample Characteristic in the isa study
    and extends the Characteristic class.
    """

    def __init__(self, category: Dict, value: str) -> None:
        super().__init__(category, value)

    @classmethod
    def from_dict(
        self, dict: Dict[str, str], characteristics_categories: Dict[str, str]
    ):
        return super().from_dict(dict, characteristics_categories)

    def to_dict(self) -> Dict[str, str]:
        return super().to_dict()
