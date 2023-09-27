import re
from typing import List, Dict, Union, Optional

from pandas import DataFrame
from ena_objects import other_material_characteristic

from ena_objects.ena_std_lib import filter_attribute_by, validate_dict
from ena_objects.characteristic import IsaBase
from ena_objects.ena_sample import EnaSample
from ena_objects.other_material_characteristic import OtherMaterialCharacteristic
from ena_objects.parameter_value import ParameterValue
from ena_objects.other_material import OtherMaterial


def experiment_alias(other_material: OtherMaterial):
    seek_assays_id: str = re.split("/", other_material.id)[1]
    return EnaExperiment.prefix + seek_assays_id


def fetch_characteristic_categories(study_dict: Dict):
    return [
        {"id": cc["@id"], "value": cc["characteristicType"]["annotationValue"]}
        for cc in study_dict["characteristicCategories"]
    ]


def get_other_materials(study_dict: Dict) -> List[OtherMaterial]:
    other_materials = []
    characteristics_categories = fetch_characteristic_categories(study_dict)
    # parameters = fetch_parameters()
    for assay in study_dict["assays"]:
        for om in assay["materials"]["otherMaterials"]:
            other_material = OtherMaterial.from_dict(
                dict=om, characteristics_categories=characteristics_categories
            )
            other_materials.append(other_material)

    return other_materials


def library_names(study_dict: Dict) -> List[str]:
    return [om["name"] for om in get_other_materials(study_dict)]


def sample_associations(assay_dict: Dict):
    process_sequence = []
    for process in assay_dict["processSequence"]:
        input_ids = [input["@id"] for input in process["inputs"]]
        output_ids = [output["@id"] for output in process["outputs"]]
        process_sequence.append({"input": input_ids, "output": output_ids})

    return process_sequence


def get_derived_sample_alias(other_material: OtherMaterial, study_dict: Dict) -> str:
    assoc_sample_ids = []
    for assay in study_dict["assays"]:
        for sa in sample_associations(assay):
            if other_material.id in sa["output"]:
                for input in sa["input"]:
                    alias = EnaSample.prefix + re.split("/", input)[-1]
                    assoc_sample_ids.append(alias)
    return assoc_sample_ids


def fetch_parameters(protocol_dict: Dict):
    parameters = []
    for protocol in protocol_dict:
        for parameter in protocol["parameters"]:
            parameters.append(
                {
                    "id": parameter["@id"],
                    "name": parameter["parameterName"]["annotationValue"],
                }
            )
    return parameters


def get_parameter_values(study_dict: Dict) -> Dict:
    param_vals = []
    parameters = fetch_parameters(study_dict["protocols"])
    for assay in study_dict["assays"]:
        for ps in assay["processSequence"]:
            sample_id = re.split("/", ps["@id"])[-1]
            parameter_values = [
                ParameterValue.from_dict(parameter_value, parameters)
                for parameter_value in ps["parameterValues"]
            ]
            param_vals.append(
                {"sample_id": sample_id, "paramter_values": parameter_values}
            )
    return param_vals


class EnaExperiment(IsaBase):
    """
    Generates an Experiment object, compliant to the requirements of ENA
    """

    mandatory_keys = [
        "protocols",
        "materials",
        "processSequence",
        "assays",
    ]
    prefix = "https://datahub.elixir-belgium.org/assays/"  # TODO: Replace by something less hard-coded

    def __init__(
        self,
        alias: str,
        study_alias: str,
        sample_alias: str,
        library_name: str,
        parameter_values: List[ParameterValue] = [],
        other_material_characteristics: List[OtherMaterialCharacteristic] = [],
    ) -> None:
        self.alias = alias
        self.study_alias = study_alias
        self.sample_alias = sample_alias
        self.library_name = library_name
        self.parameter_values = parameter_values
        self.other_material_characteristics = other_material_characteristics

    def to_dict(self) -> Dict:
        return {
            "alias": self.alias,
            "study_alias": self.sample_alias,
            "sample_alias": self.sample_alias,
            "library_name": self.library_name,
            "parameter_values": [pv for pv in self.parameter_values],
            "other_material_characteristics": [
                omc.to_dict() for omc in self.other_material_characteristics
            ],
        }

    def from_study_dict(study_dict: Dict, study_alias):
        [validate_dict(study_dict, key) for key in EnaExperiment.mandatory_keys]

        other_materials = get_other_materials(study_dict)

        # protocol_parameters = protocol_parameters(study_dict["protocols"])
        parameter_values = get_parameter_values(study_dict)

        ena_experiments = []
        for om in other_materials:
            om_id = re.split("/", om.id)[-1]
            ena_experiments.append(
                EnaExperiment(
                    alias=experiment_alias(om),
                    library_name=om.name,
                    study_alias=study_alias,
                    sample_alias=get_derived_sample_alias(om, study_dict),
                    parameter_values=list(
                        filter(lambda pv: pv["sample_id"] == om_id, parameter_values)
                    ),
                    other_material_characteristics=om.other_material_characteristics,
                )
            )
        return ena_experiments


def export_experiments_to_dataframe(experiments: List[EnaExperiment]) -> DataFrame:
    flat_dicts = []
    for experiment in experiments:
        experiment_dict = experiment.to_dict()
        other_material_characteristics = experiment_dict.pop(
            "other_material_characteristics"
        )
        # omc_dicts = [omc.to_dict() for omc in other_material_characteristics]

        parameter_values = experiment_dict.pop("parameter_values")
        # pv_dicts = [pv.to_dict() for pv in parameter_values]

        for omc in omc_dicts:
            experiment_dict.update({omc["category"]: omc["value"]})
        for pv in pv_dicts:
            experiment_dict.update({pv["category"]: pv["value"]})
        flat_dicts.append(experiment_dict)
    return DataFrame.from_dict(flat_dicts)
