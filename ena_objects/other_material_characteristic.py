from typing import Dict
from ena_objects.characteristic import Category, Characteristic, Unit, Value


class OtherMaterialCharacteristic(Characteristic):
    """
    This class represents the other material object.
    """

    def __init__(self, category: Category, value: Value, unit: Unit) -> None:
        super().__init__(category, value, unit)

    @classmethod
    def from_dict(cls, dict: Dict, characteristics_categories: Dict):
        return super().from_dict(dict, characteristics_categories)

    def to_dict(self) -> Dict:
        return super().to_dict()
