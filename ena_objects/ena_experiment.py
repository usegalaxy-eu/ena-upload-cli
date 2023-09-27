from typing import List, Dict, Union, Optional

from ena_objects.ena_std_lib import filter_attribute_by
from ena_objects.characteristic import IsaBase
from ena_objects.ena_sample import EnaSample
from ena_objects.parameter_value import ParameterValue
from ena_objects.other_material import OtherMaterial


# def filter_other_material_attribute_by(
#     data: List[Dict],
#     filter_key: str,
#     filter_val: str,
#     return_key: str,
# ) -> Union[str, int]:
#     return [
#         attribute[return_key]
#         for attribute in data
#         if attribute[filter_key] == filter_val
#     ]


def experiment_alias(assay_dict: Dict):
    prefix = "https://datahub.elixir-belgium.org/assays/"  # TODO: Replace by something less hard-coded
    seek_assays_id: str = assay_dict["@id"]
    return prefix + seek_assays_id


def fetch_characteristic_categories(study_dict: Dict):
    return [
        {"id": cc["@id"], "value": cc["characteristicType"]["annotationValue"]}
        for cc in study_dict["characteristicCategories"]
    ]


def get_other_materials(study_dict: Dict) -> List[OtherMaterial]:
    other_materials = []

    for study in study_dict["studies"]:
        for assay in study["assays"]:
            for om in assay["materials"]["otherMaterials"]:
                other_materials.append(om)

    return [
        OtherMaterial.from_dict(other_material) for other_material in other_materials
    ]


# def parameter_id(study_isa_jon: Dict, parameter_name: str) -> Optional[int]:
#     for protocol in study_isa_jon["protocols"]:
#         for parameter in protocol["parameters"]:
#             if parameter["parameterName"]["annotationValue"] == parameter_name:
#                 return parameter["@id"]


# def parameter_value(study_isa_json: Dict, parameter_name: str) -> List[any]:
#     pass


class EnaExperiment(IsaBase):
    """
    Generates an Experiment object, compliant to the requirements of ENA
    """

    mandatory_keys = [
        "alias",
        "title",
        "study",
        "sample",
        "parameter_values",
        "other_material",
    ]

    def __init__(
        self,
        alias: str,
        title: str,
        study_alias: str,
        sample_alias: str,
        library_name: str,
        ibrary_strategy,
        library_source: str,
        library_selection: str,
        library_layout: str,
        insert_size: str,
        library_construction_protocol: str,
        platform: str,
        instrument_model: str,
    ) -> None:
        self.alias = alias
        self.title = title
        self.study = study_alias
        self.sample = sample_alias
        self.library_name = library_name
        self.ibrary_strategy = ibrary_strategy
        self.library_source = library_source
        self.library_selection = library_selection
        self.library_layout = library_layout
        self.insert_size = insert_size
        self.library_construction_protocol = library_construction_protocol
        self.platform = platform
        self.instrument_model = instrument_model
