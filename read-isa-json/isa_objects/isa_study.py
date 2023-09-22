class IsaStudy:
    def __init__(
        self, alias, title, study_type, study_abstract, new_study_type=None
    ) -> None:
        self.alias = alias
        self.title = title
        self.study_type = study_type
        self.new_study_type = new_study_type
        self.study_abstract = study_abstract

    @classmethod
    def from_isa_json(isa_json):
        pass