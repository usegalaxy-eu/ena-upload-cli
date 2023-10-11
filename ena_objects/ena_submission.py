from typing import List, Dict
from numpy import append

from pandas import DataFrame
import pandas
from ena_objects.characteristic import IsaBase
from ena_objects.ena_experiment import export_experiments_to_dataframe
from ena_objects.ena_run import export_runs_to_dataframe
from ena_objects.ena_sample import export_samples_to_dataframe

from ena_objects.ena_study import EnaStudy


def merge_df_by_key(
    dataframe_dict_list: List[Dict[str, DataFrame]], key: str
) -> DataFrame:
    """Filters a list of pandas DataFrames on the provided key and merges them by row.

    Args:
        dataframe_dict_list (List[Dict[str, DataFrame]]): list of dictionary, containing the DataFrames
        key (str): key to filter the list on

    Returns:
        DataFrame: resulting DataFrame
    """
    filtered_list = list(map(lambda d: d[key], dataframe_dict_list))
    return pandas.concat(filtered_list)


def fetch_ena_studies(isa_json: Dict[str, str]) -> Dict[str, str]:
    ena_studies = []
    for study in isa_json["studies"]:
        for assay in study["assays"]:
            ena_studies.append(assay)
    return ena_studies


def fetch_assay(assay, required_assays):
    for ra in required_assays:
        for key, value in ra.items():
            for assay_comment in assay["comments"]:
                if assay_comment["name"] == key and assay_comment["value"] == value:
                    return assay


def filter_assays(
    isa_json: Dict[str, str], required_assays: List[Dict[str, str]]
) -> Dict[str, str]:
    new_studies = []
    new_isa_json = isa_json
    studies = new_isa_json.pop("studies")
    for study in studies:
        assays = study.pop("assays")
        filtered_assays = [
            fetch_assay(assay, required_assays)
            for assay in assays
            if fetch_assay(assay, required_assays) is not None
        ]
        if len(filtered_assays) > 0:
            study["assays"] = filtered_assays
            new_studies.append(study)
    new_isa_json["studies"] = new_studies
    return new_isa_json


class EnaSubmission(IsaBase):
    """
    Wrapper objects, holding studies
    """

    def __init__(
        self,
        studies: List[EnaStudy] = [],
    ) -> None:
        super().__init__()
        self.studies = studies

    def from_isa_json(
        isa_json: Dict[str, str], required_assays: List[Dict[str, str]]
    ) -> None:
        """Generates an EnaSubmission from a ISA JSON dictionary.

        Args:
            isa_json (Dict[str, str]): ISA JSON dictionary

        Returns:
            EnaSubmission: resulting EnaSubmission
        """
        filtered_isa_json: Dict[str, str] = filter_assays(isa_json, required_assays)

        return EnaSubmission(studies=EnaStudy.from_isa_json(filtered_isa_json))

    def generate_dataframes(self) -> Dict[str, DataFrame]:
        """Generates all necessary DataFrames for the ENA Upload tool
        and returns them in a dictionary.

        Returns:
            Dict[str, DataFrame]: resulting dictionary of DataFrames
        """
        dataframes = []
        for study in self.studies:
            study_df = EnaStudy.to_dataframe(study)
            samples_df = export_samples_to_dataframe(study.samples)
            experiments_df = export_experiments_to_dataframe(study.experiments)
            runs_df = export_runs_to_dataframe(study.runs)
            dataframes.append(
                {
                    "study_df": study_df,
                    "samples_df": samples_df,
                    "experiments_df": experiments_df,
                    "runs_df": runs_df,
                }
            )
        return {
            "study": merge_df_by_key(dataframes, "study_df"),
            "samples": merge_df_by_key(dataframes, "samples_df"),
            "experiments": merge_df_by_key(dataframes, "experiments_df"),
            "runs": merge_df_by_key(dataframes, "runs_df"),
        }
