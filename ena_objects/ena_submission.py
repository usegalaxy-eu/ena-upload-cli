from typing import List, Dict

from pandas import DataFrame
import pandas
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


class EnaSubmission:
    """
    Wrapper objects, holding a Study
    """

    def __init__(
        self,
        studies: List[EnaStudy] = [],
    ) -> None:
        self.studies = studies

    def from_isa_json(isa_json: Dict[str, str]) -> None:
        """Generates an EnaSubmission from a ISA JSON dictionary.

        Args:
            isa_json (Dict[str, str]): ISA JSON dictionary

        Returns:
            EnaSubmission: resulting EnaSubmission
        """
        return EnaSubmission(
            studies=EnaStudy.from_isa_json(isa_json),
        )

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
