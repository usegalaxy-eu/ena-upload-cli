from typing import List, Dict

from pandas import DataFrame

from ena_objects.characteristic import IsaBase
from ena_objects.ena_std_lib import get_assay_sample_associations, clip_off_prefix


class DataFileComment(IsaBase):
    mandatory_keys = ["name", "value"]

    def __init__(self, name: str, value: str) -> None:
        super().__init__()
        self.name = name
        self.value = value

    @classmethod
    def from_dict(self, comments_dict) -> None:
        for comment in comments_dict:
            super().check_dict_keys(dict=comment, mandatory_keys=self.mandatory_keys)

        return [
            DataFileComment(name=comment["name"], value=comment["value"])
            for comment in comments_dict
        ]

    def to_dict(self) -> Dict:
        return {"name": self.name, "value": self.value}


class DataFile(IsaBase):
    mandatory_keys = ["@id", "name", "type", "comments"]

    def __init__(self, id, name, type, comments, derived_experiment_id) -> None:
        super().__init__()
        self.id: str = id
        self.name: str = name
        self.type: str = type
        self.comments: List[DataFileComment] = comments
        self.derived_experiment_id: str = derived_experiment_id

    @classmethod
    def from_data_file_dict(self, data_file_dict: Dict, associations: Dict) -> None:
        super().check_dict_keys(data_file_dict, self.mandatory_keys)
        return DataFile(
            id=data_file_dict["@id"],
            name=data_file_dict["name"],
            type=data_file_dict["type"],
            comments=DataFileComment.from_dict(data_file_dict["comments"]),
            derived_experiment_id=get_derived_expertiment_id(
                associations, clip_off_prefix(data_file_dict["@id"])
            ),
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "comments": [comment.to_dict() for comment in self.comments],
            "derived_experiment_id": self.derived_experiment_id,
        }


def fetch_run_alias(data_file: Dict):
    return EnaRun.prefix + clip_off_prefix(data_file["@id"])


def get_derived_expertiment_id(associations: List[Dict], data_file_id: str):
    for association in associations:
        if data_file_id in clip_off_prefix(association["output"]):
            return association["input"][0]


def fetch_experiment_alias(data_file: DataFile) -> str:
    return EnaRun.prefix + clip_off_prefix(data_file.derived_experiment_id)


class EnaRun(IsaBase):
    """
    Generates a Run object, compliant to the requirements of ENA
    """

    mandatory_keys = ["dataFiles", "processSequence"]
    prefix = "https://datahub.elixir-belgium.org/samples/"  # TODO: Replace by something less hard-coded

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
    def from_study_dict(self, study_dict: Dict) -> None:
        ena_runs = []

        for assay in study_dict["assays"]:
            super().check_dict_keys(assay, self.mandatory_keys)
            sample_datafile_associations = get_assay_sample_associations(assay)
            for data_file in assay["dataFiles"]:
                current_data_file = DataFile.from_data_file_dict(
                    data_file, sample_datafile_associations
                )
                ena_runs.append(
                    EnaRun(
                        alias=fetch_run_alias(data_file),
                        experiment_alias=fetch_experiment_alias(current_data_file),
                        data_file=current_data_file,
                    )
                )

        return ena_runs

    def to_dict(self) -> Dict:
        return {
            "alias": self.alias,
            "experiment_alias": self.experiment_alias,
            "data_file": self.data_file.to_dict(),
        }


def export_runs_to_dataframe(runs: List[EnaRun]) -> DataFrame:
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
