from typing import List, Dict

from decopatch import class_decorator
from exceptiongroup import catch
from ena_objects.ena_std_lib import validate_dict


class IsaBase:
    """
    This is the base class
    """

    @classmethod
    def check_dict_keys(self, dict: Dict[str, str], mandatory_keys):
        [validate_dict(dict=dict, key=key) for key in mandatory_keys]


def fetch_category_name(categories: Dict[str, str], name: str) -> str:
    for cat in categories:
        if name["@id"] == cat["id"]:
            if "name" in cat:
                return cat["name"]
            elif "value" in cat:
                return cat["value"]


def category_dict(dict: Dict[str, str], categories: Dict[str, str]):
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
    def from_dict(self, dict: Dict[str, str], categories: Dict[str, str]):
        super().check_dict_keys(dict, self.mandatory_keys)
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
    This class represents the other material object.
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
    and is inherited from the Characteristic class
    """

    def __init__(self, category: Dict[str, str], value: str) -> None:
        super().__init__(category, value)

    @classmethod
    def from_dict(self, dict: Dict[str, str], parameters: Dict[str, str]):
        return super().from_dict(dict, parameters)

    def to_dict(self) -> Dict[str, str]:
        return super().to_dict()


class SampleCharacteristic(Characteristic):
    def __init__(self, category: Dict, value: str) -> None:
        super().__init__(category, value)

    @classmethod
    def from_dict(
        self, dict: Dict[str, str], characteristics_categories: Dict[str, str]
    ):
        return super().from_dict(dict, characteristics_categories)

    def to_dict(self) -> Dict[str, str]:
        return super().to_dict()
