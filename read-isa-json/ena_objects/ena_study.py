from typing import List, Optional, Dict
from pandas import DataFrame


def study_publication_ids(publication_isa_json) -> List[int]:
    return [pub["id"] for pub in publication_isa_json]


def validate_isa_json(isa_json: Dict, key: str) -> None:
    if not key in isa_json.keys():
        raise KeyError(f"{key} was not found in the provided ISA JSON.")


class EnaStudy:
    def __init__(
        self,
        alias: str,
        title: str,
        study_type: str,
        study_abstract: str,
        new_study_type=Optional[str],
        pubmed_id=Optional[List[int]],
    ) -> None:
        self.alias = alias
        self.title = title
        self.study_type = study_type
        self.new_study_type = new_study_type
        self.study_abstract = study_abstract
        self.pubmed_id = pubmed_id

    def from_isa_json(isa_json):
        mandatory_keys = ["title", "description", "publications"]
        [validate_isa_json(isa_json, key) for key in mandatory_keys]

        return [
            EnaStudy(
                alias="",  # TODO: Add SEEK URL of Study
                title=study["title"],
                study_type="",  # TODO: Replace by Custom metadata of the Assay level
                study_abstract=study["description"],
                pubmed_id=study_publication_ids(
                    publication_isa_json=study["publications"]
                ),
            )
            for study in isa_json["studies"]
        ]

    def to_dataframe(self) -> DataFrame:
        """
        Dumps the study object in a pandas DataFrame of the object
        """
        return DataFrame.from_dict(vars(self))
