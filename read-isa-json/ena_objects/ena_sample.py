from typing import List, Dict


class EnaSample:
    """
    Generates an Sample object, compliant to the requirements of ENA
    """

    def __init__(
        self,
        alias: str,
        status: str,
        taxon_id: int,
        sample_description: str,
    ) -> None:
        self.alias = alias
        self.status = status
        self.taxon_id = taxon_id
        self.sample_description = sample_description
