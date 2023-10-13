from ena_objects.characteristic import (
    IsaBase,
    ParameterValue,
    OtherMaterialCharacteristic,
)

from typing import List, Dict


class OtherMaterial(IsaBase):
    """
    This Class represents an 'other_material' in the ISA JSON and extends the ISA Base class.
    """

    def __init__(
        self,
        id: int,
        name: str,
        type: str,
        other_material_characteristics: OtherMaterialCharacteristic,
    ) -> None:
        self.id = id
        self.name = name
        self.type = type
        self.other_material_characteristics = other_material_characteristics

    @classmethod
    def from_dict(
        cls, dict: Dict[str, str], characteristics_categories: List[Dict[str, str]]
    ) -> None:
        """Constructs an OtherMaterial, starting from a other_material dictionary
        and a list of all other_material_characteristics.

        Args:
            dict (Dict[str, str]): other_material dictionary
            characteristics_categories (List[Dict[str, str]]): other_material_characteristics dictionary

        Returns:
            OtherMaterial: other material object
        """
        return OtherMaterial(
            id=dict["@id"],
            name=dict["name"],
            type=dict["type"],
            other_material_characteristics=[
                OtherMaterialCharacteristic.from_dict(char, characteristics_categories)
                for char in dict["characteristics"]
            ],
        )
