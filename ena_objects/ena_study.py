from operator import index
from typing import List, Optional, Dict
from pandas import DataFrame
from ena_objects.characteristic import IsaBase
from ena_objects.ena_experiment import EnaExperiment
from ena_objects.ena_run import EnaRun
from ena_objects.ena_sample import EnaSample
from ena_objects.ena_std_lib import (
    fetch_assay_streams,
    fetch_assay_comment_by_name,
    get_study_id,
)


def study_publication_ids(publication_isa_json: Dict) -> List[int]:
    """Retrieves the pubmed_ids from the ISA JSON

    Args:
        publication_isa_json (Dict): Publication part of the ISA JSON dictionary

    Returns:
        List[int]: List of pubmed ID's
    """
    return ",".join([str(pub["pubMedID"]) for pub in publication_isa_json])


def study_alias(assay_stream: Dict[str, str], seek_study_id) -> str:
    """Creates a study_alias, based on information of the assay stream and study of the ISA JSON.

    Args:
        assay_stream Dict[str, str]: assay stream part of the ISA JSON
        seek_study_id str: Study ID

    Returns:
        str: the study_alias
    """
    prefix = fetch_assay_comment_by_name(assay_stream, EnaStudy.prefix)["value"]
    return prefix + seek_study_id


def study_title(assay_stream: Dict[str, str]) -> str:
    return fetch_assay_comment_by_name(assay_stream, "ena_study_title")["value"]


def study_type(assay_stream: Dict[str, str]) -> str:
    return fetch_assay_comment_by_name(assay_stream, "study_type")["value"]


def new_study_type(assay_stream: Dict[str, str]) -> str:
    if study_type(assay_stream).lower() != "other":
        return None

    return fetch_assay_comment_by_name(assay_stream, "new_study_type")["value"]


def study_abstract(assay_stream: Dict[str, str]) -> str:
    return fetch_assay_comment_by_name(assay_stream, "ena_study_abstract")["value"]


class EnaStudy(IsaBase):
    """Generates a Study object, compliant to the requirements of ENA"""

    mandatory_keys = ["title", "description", "publications"]
    prefix = "ena_study_alias_prefix"

    def __init__(
        self,
        alias: str,
        title: str,
        study_type: str,
        study_abstract: str,
        samples: List[EnaSample],
        experiments: List[EnaExperiment] = [],
        runs: List[EnaRun] = [],
        new_study_type: Optional[str] = None,
        pubmed_id: Optional[str] = None,
    ) -> None:
        self.alias = alias
        self.title = title
        self.study_type = study_type
        self.new_study_type = new_study_type
        self.study_abstract = study_abstract
        self.new_study_type = new_study_type
        self.pubmed_id = pubmed_id

        self.samples = samples
        self.experiments = experiments
        self.runs = runs

    def to_dict(self):
        return {
            "alias": self.alias,
            "title": self.title,
            "study_type": self.study_type,
            "study_abstract": self.study_abstract,
            "new_study_type": self.new_study_type,
            "pubmed_id": self.pubmed_id,
        }

    @classmethod
    def from_isa_json(self, isa_json: Dict[str, str]):
        """Method that creates an EnaStudy with params from ISA JSON Dictionary

        Args:
            isa_json: ISA JSON Dict

        Returns:
            EnaStudy: EnaStudy object
        """
        super().check_dict_keys(isa_json, self.mandatory_keys)

        ena_studies = []
        for study in isa_json["studies"]:
            assay_streams = fetch_assay_streams(study)
            study_id = get_study_id(study)
            for assay_stream in assay_streams:
                current_study_alias = study_alias(assay_stream, study_id)
                ena_studies.append(
                    EnaStudy(
                        alias=current_study_alias,
                        title=study_title(assay_stream),
                        study_type=study_type(assay_stream),
                        study_abstract=study_abstract(assay_stream),
                        new_study_type=new_study_type(assay_stream),
                        samples=EnaSample.from_study_dict(study),
                        experiments=EnaExperiment.from_study_dict(
                            study, current_study_alias
                        ),
                        runs=EnaRun.from_study_dict(assay_stream),
                        pubmed_id=study_publication_ids(
                            publication_isa_json=study["publications"]
                        ),
                    )
                )

        return ena_studies

    def to_dataframe(self) -> DataFrame:
        """Dumps the study object in a pandas DataFrame of the object

        Returns:
            DataFrame: Pandas DataFrame representation of the Study
        """
        return DataFrame.from_dict([self.to_dict()])
