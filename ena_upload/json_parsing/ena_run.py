from typing import List, Dict

from pandas import DataFrame

from ena_upload.json_parsing.characteristic import IsaBase
from ena_upload.json_parsing.ena_experiment import EnaExperiment
from ena_upload.json_parsing.ena_std_lib import (
    fetch_assay_comment_by_name,
    get_assay_sample_associations,
    clip_off_prefix,
)


class DataFileComment(IsaBase):
    """Object representation of a data file comment in the ISA JSON.
    Extends the IsaBase class.
    """

    mandatory_keys = ["name", "value"]

    def __init__(self, name: str, value: str) -> None:
        super().__init__()
        self.name = name
        self.value = value

    @classmethod
    def from_dict(self, comments_dict: Dict[str, str]) -> None:
        """Generates a DataFileComment from comment dictionary.

        Args:
            comments_dict (Dict[str, str]): Input data file comment dictionary

        Returns:
            DataFileComment: Resulting DataFileComment
        """
        return [
            DataFileComment(name=comment["name"], value=comment["value"])
            for comment in comments_dict
        ]

    def to_dict(self) -> Dict:
        return {"name": self.name, "value": self.value}


class DataFile(IsaBase):
    """Object representation of a data file in the ISA JSON.
    Extends the IsaBase class.
    """

    def __init__(self, id, name, type, comments, derived_experiment_id) -> None:
        super().__init__()
        self.id: str = id
        self.name: str = name
        self.type: str = type
        self.comments: List[DataFileComment] = comments
        self.derived_experiment_id: str = derived_experiment_id

    @classmethod
    def from_data_file_dict(
        self, data_file_dict: Dict[str, str], associations: Dict[str, str]
    ) -> None:
        """Generates a DataFile from a data file dictionary and dictionary of data file associations.

        Args:
            data_file_dict (Dict[str, str]): data file dictionary
            associations (Dict[str, str]): data file associations dictionar

        Returns:
            DataFile: Resulting DataFile
        """
        return DataFile(
            id=data_file_dict["@id"],
            name=data_file_dict["name"],
            type=data_file_dict["type"],
            comments=DataFileComment.from_dict(data_file_dict["comments"]),
            derived_experiment_id=get_derived_expertiment_id(
                associations, clip_off_prefix(data_file_dict["@id"])
            ),
        )

    def to_dict(self) -> Dict[str, str]:
        """Converts the DataFile object into a dictionary.

        Returns:
            Dict[str, str]: Resulting dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "comments": [comment.to_dict() for comment in self.comments],
            "derived_experiment_id": self.derived_experiment_id,
        }


def get_involved_process_id(id: str, process_sequence: List[Dict[str, str]]):
    for process in process_sequence:
        output_ids = [output["@id"] for output in process["outputs"]]
        if id in output_ids:
            return process["@id"]


def run_alias(
    data_file: Dict[str, str], process_sequence: List[Dict[str, str]], prefix: str
) -> str:
    """Generates an alias for the run, based on the data file dictionary
    and prefix specified in the Class

    Args:
        data_file (Dict[str, str]): Input data file dictionary
        prefix (str): prefix for alias

    Returns:
        str: Resulting alias
    """

    data_file_id = data_file["@id"]
    process_id = get_involved_process_id(data_file_id, process_sequence)
    return prefix + clip_off_prefix(process_id)


def get_derived_expertiment_id(
    associations: List[Dict[str, str]], data_file_id: str
) -> str:
    """Fetches the derived sample id from data file id and a list of datafile - experiment associations.

    Args:
        associations (List[Dict[str, str]]): list of sample - experiment associations
        data_file_id (str): data file id

    Returns:
        str: resulting derived experiment id
    """
    for association in associations:
        if data_file_id in clip_off_prefix(association["output"]):
            return association["input"][0]


def fetch_experiment_alias(data_file: DataFile, prefix: str) -> str:
    """Generates the experiment alias from the information in the provided data file.

    Args:
        data_file (DataFile): Input data file

    Returns:
        str: associated experiment alias
    """
    return prefix + clip_off_prefix(data_file.derived_experiment_id)


class EnaRun(IsaBase):
    """
    Generates a Run object, compliant to the requirements of ENA.
    """

    prefix = "ena_run_alias_prefix"

    def __init__(
        self,
        alias: str,
        experiment_alias: str,
        data_file: DataFile,
    ) -> None:
        super().__init__()
        self.alias = alias
        self.experiment_alias = experiment_alias
        self.data_file = data_file

    @classmethod
    def from_assay_stream(self, assay_stream: Dict[str, str]) -> None:
        """Generates a EnaRun object from a study dictionary.

        Args:
            study_dict (Dict[str, str]): Input study dictionary

        Returns:
            EnaRun: Resulting run
        """
        ena_runs = []

        sample_datafile_associations = get_assay_sample_associations(assay_stream)
        prefix = fetch_assay_comment_by_name(assay_stream, EnaRun.prefix)["value"]
        ena_experiment_prefix = fetch_assay_comment_by_name(
            assay_stream, EnaExperiment.prefix
        )["value"]
        for data_file in assay_stream["dataFiles"]:
            current_data_file = DataFile.from_data_file_dict(
                data_file, sample_datafile_associations
            )
            ena_runs.append(
                EnaRun(
                    alias=run_alias(data_file, assay_stream["processSequence"], prefix),
                    experiment_alias=fetch_experiment_alias(
                        current_data_file, ena_experiment_prefix
                    ),
                    data_file=current_data_file,
                )
            )

        return ena_runs

    def to_dict(self) -> Dict[str, str]:
        """Converts the EnaRun object into a dictionary

        Returns:
            Dict[str, str]: resulting dictionary
        """
        return {
            "alias": self.alias,
            "experiment_alias": self.experiment_alias,
            "data_file": self.data_file.to_dict(),
        }


def export_runs_to_dataframe(runs: List[EnaRun]) -> DataFrame:
    """Exports a list of EnaRun to a pandas DataFrame

    Args:
        runs (List[EnaRun]): input list of EnaRun

    Returns:
        DataFrame: Resulting pandas DataFrame
    """
    ena_run_dicts = [run.to_dict() for run in runs]
    flat_dicts = []
    for dict in ena_run_dicts:
        data_file = dict.pop("data_file")
        data_file_comments = data_file.pop("comments")
        dict.update({"file_name": data_file["name"]})
        for dfc in data_file_comments:
            dict.update({dfc["name"]: dfc["value"]})
        flat_dicts.append(dict)
    return DataFrame.from_dict(flat_dicts)
