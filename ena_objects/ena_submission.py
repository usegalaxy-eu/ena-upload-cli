from typing import List, Dict
from numpy import append

from pandas import DataFrame
import pandas
from ena_objects.characteristic import IsaBase
from ena_objects.ena_experiment import EnaExperiment, export_experiments_to_dataframe
from ena_objects.ena_run import EnaRun, export_runs_to_dataframe
from ena_objects.ena_sample import EnaSample, export_samples_to_dataframe
from ena_objects.ena_std_lib import fetch_assay_streams, study_publication_ids

from ena_objects.ena_study import EnaStudy, export_studies_to_dataframe


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
        samples: List[EnaSample] = [],
        experiments: List[EnaExperiment] = [],
        runs: List[EnaRun] = [],
    ) -> None:
        super().__init__()
        self.studies = studies
        self.samples = samples
        self.experiments = experiments
        self.runs = runs

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
        samples = []
        studies = []
        experiments = []
        runs = []
        for study in filtered_isa_json["studies"]:
            [samples.append(sample) for sample in EnaSample.from_study_dict(study)]

            pubmed_ids = study_publication_ids(
                publication_isa_json=study["publications"]
            )
            current_study_protocols_dict = study["protocols"]
            assay_streams = fetch_assay_streams(study)
            for assay_stream in assay_streams:
                study = EnaStudy.from_assay_stream(assay_stream, pubmed_ids)
                studies.append(study)

                [
                    experiments.append(experiment)
                    for experiment in EnaExperiment.from_assay_stream(
                        assay_stream, study.alias, current_study_protocols_dict
                    )
                ]

                [runs.append(run) for run in EnaRun.from_assay_stream(assay_stream)]

        return EnaSubmission(
            studies=studies, samples=samples, experiments=experiments, runs=runs
        )

    def generate_dataframes(self) -> Dict[str, DataFrame]:
        """Generates all necessary DataFrames for the ENA Upload tool
        and returns them in a dictionary.

        Returns:
            Dict[str, DataFrame]: resulting dictionary of DataFrames
        """
        return {
            "study": export_studies_to_dataframe(self.studies),
            "samples": export_samples_to_dataframe(self.samples),
            "experiments": export_experiments_to_dataframe(self.experiments),
            "runs": export_runs_to_dataframe(self.runs),
        }
