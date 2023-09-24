from typing import List, Dict
from ena_objects.ena_study import EnaStudy
from ena_objects.ena_sample import EnaSample


class EnaExperiment:
    """
    Generates an Experiment object, compliant to the requirements of ENA
    """

    def __init__(
        self,
        alias: str,
        title: str,
        study: EnaStudy,
        sample: EnaSample,
        library_name: str,
        ibrary_strategy,
        library_source: str,
        library_selection: str,
        library_layout: str,
        insert_size: str,
        library_construction_protocol: str,
        platform: str,
        instrument_model: str,
    ) -> None:
        self.alias = alias
        self.title = title
        self.study = study
        self.sample = sample
        self.library_name = library_name
        self.ibrary_strategy = ibrary_strategy
        self.library_source = library_source
        self.library_selection = library_selection
        self.library_layout = library_layout
        self.insert_size = insert_size
        self.library_construction_protocol = library_construction_protocol
        self.platform = platform
        self.instrument_model = instrument_model
