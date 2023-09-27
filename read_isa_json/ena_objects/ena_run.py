from typing import List, Dict
from ena_objects.ena_experiment import EnaExperiment


class EnaRun:
    """
    Generates a Run object, compliant to the requirements of ENA
    """

    def __init__(
        self,
        alias: str,
        experiments: List[EnaExperiment],
        filename: str,
        file_type: str,
    ) -> None:
        self.alias = alias
        self.experiments = experiments
        self.filename = filename
        self.file_type = file_type
