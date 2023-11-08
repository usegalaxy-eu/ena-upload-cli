from typing import List, Dict
from ena_upload.json_parsing.characteristic import SampleCharacteristic, ParameterValue

from pandas import DataFrame

from ena_upload.json_parsing.ena_std_lib import (
    clip_off_prefix,
    fetch_study_comment_by_name,
    get_parameter_values,
)


def fetch_characteristic_categories(study_dict: Dict) -> Dict:
    """Retrieves the name of a characteristic id

    Args:
        study_dict (Dict): study dictionary
        id (str): characteristic ID

    Returns:
        Dict: characteristic name corresponding with the ID
    """
    return [
        {"id": cc["@id"], "name": cc["characteristicType"]["annotationValue"]}
        for cc in study_dict["characteristicCategories"]
    ]


def fetch_characteristics(sample_dict: Dict, study_dict: Dict) -> List[Dict]:
    """Fetches the characteristics from the given sample dictionary

    Args:
        sample_dict (Dict): sample dictionary
        study_dict (Dict): study dictionary

    Returns:
        List[Dict]: List of characteristic dictionaries
    """
    characteristic_categories = fetch_characteristic_categories(study_dict)
    return [
        SampleCharacteristic.from_dict(char, characteristic_categories)
        for char in sample_dict["characteristics"]
    ]


def associated_source(sample_dict: Dict, study_dict: Dict) -> List[str]:
    """Retrieves the ID of the source associated with the given sample

    Args:
        sample_dict (Dict): sample dictionary
        study_dict (Dict): study dictionary

    Returns:
        List[str]: List of source ID's
    """
    sample_id = sample_dict["@id"]
    for process in study_dict["processSequence"]:
        input_ids = [input["@id"] for input in process["inputs"]]
        output_ids = [output["@id"] for output in process["outputs"]]
        if sample_id in output_ids:
            return input_ids


def associated_source_characteristics(sources_data: Dict, ids: List[str]) -> Dict:
    """Retrieves the characteristics of the associated sources,
    corresponding with the provided sample ID's

    Args:
        sources_data (Dict): dictionary of the sources
        ids (List[str]): list of sample ID's

    Returns:
        Dict: the dictionary of the source characteristics
    """
    for sd in sources_data:
        if sd["id"] in ids:
            return sd["characteristics"]


def sample_alias(id: str, prefix) -> str:
    """Retrieves the sample's alias

    Args:
        id (str): Sample ID

    Returns:
        str: Unique string representation of the alias
    """
    return prefix + clip_off_prefix(id)


class EnaSample:
    """
    Generates an Sample object, compliant to the requirements of ENA
    """

    prefix: str = "ena_sample_alias_prefix"

    def __init__(
        self,
        characteristics: List[SampleCharacteristic],
        parameter_values: List[ParameterValue],
        alias: str,
    ) -> None:
        self.alias = alias
        self.characteristics = characteristics
        self.parameter_values = parameter_values

    def to_dict(self) -> Dict:
        return {
            "alias": self.alias,
            "characteristics": [char.to_dict() for char in self.characteristics],
            "parameter_values": [pv.to_dict() for pv in self.parameter_values],
        }

    @classmethod
    def from_study_dict(self, study_dict: Dict) -> None:
        """Generate sample objects from a study dictionary

        Args:
            study_dict (Dict): study dictionary

        Returns:
            List[EnaSample]: List of Ena Sample objects
        """
        sources_data = [
            {
                "id": source["@id"],
                "name": source["name"],
                "characteristics": fetch_characteristics(source, study_dict),
            }
            for source in study_dict["materials"]["sources"]
        ]
        parameter_values = get_parameter_values(
            process_sequence=study_dict["processSequence"],
            study_protocols_dict=study_dict["protocols"],
        )

        samples_data = []
        for sample in study_dict["materials"]["samples"]:
            filtered_parameter_vals = list(
                filter(
                    lambda pv: pv["sample_id"] == clip_off_prefix(sample["@id"]),
                    parameter_values,
                )
            )
            parameter_vals = []
            for fpv in filtered_parameter_vals:
                for pv in fpv["parameter_values"]:
                    parameter_vals.append(pv)

            samples_data.append(
                {
                    "id": sample["@id"],
                    "name": sample["name"],
                    "characteristics": fetch_characteristics(sample, study_dict),
                    "parameter_values": parameter_vals,
                    "source": associated_source(sample, study_dict),
                }
            )

        for sd in samples_data:
            for sc in associated_source_characteristics(sources_data, sd["source"]):
                sd["characteristics"].append(sc)

        study_alias_prefix = fetch_study_comment_by_name(study_dict, self.prefix)[
            "value"
        ]
        return [
            EnaSample(
                alias=sample_alias(sd["id"], study_alias_prefix),
                characteristics=sd["characteristics"],
                parameter_values=sd["parameter_values"],
            )
            for sd in samples_data
        ]


def export_samples_to_dataframe(samples: List[EnaSample]):
    """Exports a list of Ena Samples to a pandas DataFrame

    Args:
        samples (List[EnaSample]): Ena sample list

    Returns:
        DataFrame: pandas DataFrame
    """
    flat_dicts = []
    for sample in samples:
        sample_dict = sample.to_dict()
        characteristics = sample_dict.pop("characteristics")
        for char in characteristics:
            sample_dict.update({char["category"]["name"]: char["value"]})
        parameter_values = sample_dict.pop("parameter_values")
        for pv in parameter_values:
            sample_dict.update({pv["category"]["name"]: pv["value"]})
        flat_dicts.append(sample_dict)

    return DataFrame.from_dict(flat_dicts)
