from typing import Dict
from ena_objects.characteristic import Category, Characteristic, Unit, Value


class ParameterValue(Characteristic):
    """
    This class represents a paramenter value in the isa study
    and is inherited from the Characteristic class
    """

    def __init__(self, category: Category, value: Value, unit: Unit) -> None:
        super().__init__(category, value, unit)

    def from_dict(self, dict: Dict):
        return super().from_dict(dict)
