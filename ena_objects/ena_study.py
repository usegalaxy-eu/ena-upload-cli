from typing import List, Optional, Dict
from pandas import DataFrame
from ena_objects.characteristic import IsaBase
from ena_objects.ena_std_lib import (
    clip_off_prefix,
    fetch_assay_comment_by_name,
)


def study_alias(assay_stream: Dict[str, str]) -> str:
    """Creates a study_alias, based on information of the assay stream and study of the ISA JSON.

    Args:
        assay_stream Dict[str, str]: assay stream part of the ISA JSON
        seek_study_id str: Study ID

    Returns:
        str: the study_alias
    """
    assay_stream_id = clip_off_prefix(assay_stream["@id"])
    prefix = fetch_assay_comment_by_name(assay_stream, EnaStudy.prefix)["value"]
    return prefix + assay_stream_id


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

    prefix = "ena_study_alias_prefix"

    def __init__(
        self,
        alias: str,
        title: str,
        study_type: str,
        study_abstract: str,
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
    def from_assay_stream(self, assay_stream: Dict[str, str], pubmed_ids):
        """Method that creates an EnaStudy with params from ISA JSON Dictionary

        Args:
            isa_json: ISA JSON Dict

        Returns:
            EnaStudy: EnaStudy object
        """
        return EnaStudy(
            alias=study_alias(assay_stream),
            title=study_title(assay_stream),
            study_type=study_type(assay_stream),
            study_abstract=study_abstract(assay_stream),
            new_study_type=new_study_type(assay_stream),
            pubmed_id=pubmed_ids,
        )


def export_studies_to_dataframe(studies: List[EnaStudy]) -> DataFrame:
    """Dumps the study objects in a pandas DataFrame

    Returns:
        DataFrame: Pandas DataFrame representation of the Studies
    """
    return DataFrame.from_dict([study.to_dict() for study in studies])
