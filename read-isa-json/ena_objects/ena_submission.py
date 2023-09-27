from typing import List, Dict

from ena_objects.ena_study import EnaStudy


class EnaSubmission:
    """
    Generates a Submission object, compliant to the requirements of ENA
    """

    def __init__(
        self,
        studies: List[EnaStudy] = [],
    ) -> None:
        self.studies = studies

    def from_isa_json(isa_json: Dict) -> None:
        return EnaSubmission(
            studies=EnaStudy.from_isa_json(isa_json),
        )

    def generate_dataframes():
        pass
