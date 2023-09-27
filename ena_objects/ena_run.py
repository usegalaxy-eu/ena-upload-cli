from typing import List, Dict


class EnaRun:
    """
    Generates a Run object, compliant to the requirements of ENA
    """

    def __init__(
        self,
        alias: str,
        experiment_alias: str,
        filename: str,
        file_type: str,
    ) -> None:
        self.alias = alias
        self.experiments = experiment_alias
        self.filename = filename
        self.file_type = file_type
