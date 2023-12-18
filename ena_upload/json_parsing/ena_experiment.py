from typing import List, Dict, Union

from pandas import DataFrame

from ena_upload.json_parsing.ena_std_lib import (
    fetch_assay_comment_by_name,
    get_assay_sample_associations,
    clip_off_prefix,
    get_parameter_values,
)
from ena_upload.json_parsing.characteristic import (
    IsaBase,
    OtherMaterialCharacteristic,
    ParameterValue,
)
from ena_upload.json_parsing.other_material import OtherMaterial


def experiment_alias(other_material: OtherMaterial, prefix: str) -> str:
    """Generates an alias for the experiment, starting from an other_material
    and a prefix.

    Args:
        other_material (OtherMaterial): OtherMaterial object
        prefix (str): Prefix

    Returns:
        str: experiment alias
    """
    seek_assays_id: str = clip_off_prefix(other_material.id)
    return prefix + seek_assays_id


def fetch_characteristic_categories(
    assay_stream: Dict[str, str]
) -> List[Dict[str, str]]:
    """Fetches all characteristics categories from a provided study dictionary
    and returns them as a list of characteristics categories.

    Args:
        study_dict (Dict[str, str]): Input study dictionary

    Returns:
        List[Dict[str, str]]: List of the characteristics categories
    """
    categories = []
    for cc in assay_stream["characteristicCategories"]:
        categories.append(
            {"id": cc["@id"], "value": cc["characteristicType"]["annotationValue"]}
        )
    return categories


def get_other_materials(assay_stream: Dict[str, str]) -> List[OtherMaterial]:
    """Returns a List of 'other materials' from a study dictionary
    and returns them as a list of OtherMaterial objects.

    Args:
        study_dict (Dict[str, str]): Input study dictionary

    Returns:
        List[OtherMaterial]: Resulting list of OtherMaterial objects
    """
    other_materials = []
    characteristics_categories = fetch_characteristic_categories(assay_stream)
    for om in assay_stream["materials"]["otherMaterials"]:
        other_material = OtherMaterial.from_dict(
            dict=om, characteristics_categories=characteristics_categories
        )
        other_materials.append(other_material)

    return other_materials


def library_names(study_dict: Dict[str, str]) -> List[str]:
    """Returns a list of library names from a study dictionary.

    Args:
        study_dict (Dict[str, str]): Input study dictionary

    Returns:
        List[str]: Resulting list of library names
    """
    return [om["name"] for om in get_other_materials(study_dict)]


def get_derived_sample_alias(
    other_material: OtherMaterial,
    assay_stream: Dict[str, str],
    sample_alias_prefix: str,
    return_multiple: bool = False,
) -> Union[str, List[str]]:
    """Gets Sample ids, an 'other material' is derived from.

    Args:
        other_material (OtherMaterial): other material
        study_dict (Dict): Input study dictioary
        return_multiple (bool, optional): Optional flag to return multiple sample ID's per 'other material'. Defaults to False.

    Returns:
        str: Resulting derived sample id or list of derived sample id's
    """
    assoc_sample_ids = []
    sample_associations = get_assay_sample_associations(assay_stream)
    for sa in sample_associations:
        if clip_off_prefix(other_material.id) in clip_off_prefix(sa["output"]):
            # sa["output"] => '#sample/<id>'
            # other_material.id => '#other_material/<id>'
            if return_multiple:
                for input in sa["input"]:
                    alias = sample_alias_prefix + clip_off_prefix(input)
                    assoc_sample_ids.append(alias)
            else:
                input = sa["input"][0]
                return sample_alias_prefix + clip_off_prefix(input)
    return assoc_sample_ids


class EnaExperiment(IsaBase):
    """
    Generates an Experiment object, compliant to the requirements of ENA
    """

    prefix = "ena_experiment_alias_prefix"

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

    def to_dict(self) -> Dict[str, str]:
        """Returns the EnaExperiment object as a dictionary.

        Returns:
            Dict[str, str]: Resulting dictionary with EnaExperiment information
        """
        return {
            "alias": self.alias,
            "study_alias": self.study_alias,
            "sample_alias": self.sample_alias,
            "library_name": self.library_name,
            "parameter_values": [pv.to_dict() for pv in self.parameter_values],
            "other_material_characteristics": [
                omc.to_dict() for omc in self.other_material_characteristics
            ],
        }

    @classmethod
    def from_assay_stream(
        self,
        assay_stream: Dict[str, str],
        study_alias: str,
        sample_alias_prefix: str,
        protocols_dict: Dict[str, str],
    ) -> None:
        """Generates a EnaExperiment object from a study dictionary.

        Args:
            study_dict (Dict[str, str]): Input study dictionary
            study_alias (str): Alias of the study associated with the experiments

        Returns:
            EnaExperiment: Resulting EnaExperiment object
        """

        other_materials = get_other_materials(assay_stream)
        parameter_values = get_parameter_values(
            assay_stream["processSequence"], protocols_dict
        )
        prefix = fetch_assay_comment_by_name(assay_stream, EnaExperiment.prefix)[
            "value"
        ]
        ena_experiments = []
        for om in other_materials:
            om_id = clip_off_prefix(om.id)
            s_alias = get_derived_sample_alias(om, assay_stream, sample_alias_prefix)
            filtered_parameter_vals = list(
                filter(lambda pv: pv["sample_id"] == om_id, parameter_values)
            )

            parameter_vals = []
            for fpv in filtered_parameter_vals:
                for pv in fpv["parameter_values"]:
                    parameter_vals.append(pv)

            ena_experiments.append(
                EnaExperiment(
                    alias=experiment_alias(om, prefix),
                    library_name=om.name,
                    study_alias=study_alias,
                    sample_alias=s_alias,
                    parameter_values=parameter_vals,
                    other_material_characteristics=om.other_material_characteristics,
                )
            )
        return ena_experiments


def export_experiments_to_dataframe(experiments: List[EnaExperiment]) -> DataFrame:
    """Exports the information out of a list of EnaExperiment to a pandas DataFrame

    Args:
        experiments (List[EnaExperiment]): Input list of experiments

    Returns:
        DataFrame: Resulting DataFrame
    """
    flat_dicts = []
    for experiment in experiments:
        experiment_dict = experiment.to_dict()
        other_material_characteristics = experiment_dict.pop(
            "other_material_characteristics"
        )

        parameter_values = experiment_dict.pop("parameter_values")

        for omc in other_material_characteristics:
            experiment_dict.update({omc["category"]["name"]: omc["value"]})

        for pv in parameter_values:
            experiment_dict.update({pv["category"]["name"]: pv["value"]})

        flat_dicts.append(experiment_dict)

    return DataFrame.from_dict(flat_dicts)
