from typing import List, Dict
from ena_objects.ena_run import EnaRun


class EnaSubmission:
    """
    Generates a Submission object, compliant to the requirements of ENA
    """

    def __init__(self, runs: List[EnaRun]) -> None:
        self.runs = runs
