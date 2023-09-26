from typing import Dict
from ena_objects.characteristic import Category, Characteristic, Unit, Value


class OtherMaterialCharacteristic(Characteristic):
    """
    This class represents the other material object.
    """

    def __init__(self, category: Category, value: Value, unit: Unit) -> None:
        super().__init__(category, value, unit)

    def from_dict(self, dict: Dict):
        return super().from_dict(dict)
