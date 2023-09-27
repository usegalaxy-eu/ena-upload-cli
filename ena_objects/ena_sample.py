import re
from typing import List, Dict

from pandas import DataFrame


def study_characteristic_category_name(study_dict: Dict, id: str) -> Dict:
    """Retrieves the name of a characteristic id

    Args:
        study_dict (Dict): study dictionary
        id (str): characteristic ID

    Returns:
        Dict: characteristic name corresponding with the ID
    """
    char_cat_dicts = [
        {"id": cc["@id"], "name": cc["characteristicType"]["annotationValue"]}
        for cc in study_dict["characteristicCategories"]
    ]

    for ccd in char_cat_dicts:
        if ccd["id"] == id:
            return ccd["name"]


def fetch_characteristics(sample_dict: Dict, study_dict: Dict) -> List[Dict]:
    """Fetches the characteristics from the given sample dictionary

    Args:
        sample_dict (Dict): sample dictionary
        study_dict (Dict): study dictionary

    Returns:
        List[Dict]: List of characteristic dictionaries
    """
    return [
        {
            "category_id": char["category"]["@id"],
            "category_name": study_characteristic_category_name(
                study_dict, char["category"]["@id"]
            ),
            "value": char["value"]["annotationValue"],
        }
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


def sample_alias(id: str) -> str:
    """Retrieves the sample's alias

    Args:
        id (str): Sample ID

    Returns:
        str: Unique string representation of the alias
    """

    sample_id = re.split("/", id)[1]
    return EnaSample.prefix + sample_id


class EnaSample:
    """
    Generates an Sample object, compliant to the requirements of ENA
    """

    prefix: str = "https://datahub.elixir-belgium.org/samples/"  # TODO: Replace by something less hard-coded

    def __init__(self, characteristics: Dict, alias: str) -> None:
        self.alias = alias
        self.characteristics = characteristics

    def to_dict(self) -> Dict:
        return {
            "alias": self.alias,
            "characteristics": self.characteristics,
        }

    def from_study_dict(study_dict: Dict) -> None:
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

        samples_data = [
            {
                "id": sample["@id"],
                "name": sample["name"],
                "characteristics": fetch_characteristics(sample, study_dict),
                "source": associated_source(sample, study_dict),
            }
            for sample in study_dict["materials"]["samples"]
        ]

        for sd in samples_data:
            for sc in associated_source_characteristics(sources_data, sd["source"]):
                sd["characteristics"].append(sc)

        return [
            EnaSample(
                alias=sample_alias(sd["id"]),
                characteristics=sd["characteristics"],
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
            sample_dict.update({char["category_name"]: char["value"]})
        flat_dicts.append(sample_dict)

    return DataFrame.from_dict(flat_dicts)
