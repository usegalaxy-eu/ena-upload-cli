from ast import List, ClassDef
from typing import Dict


def filter_attribute_by(attribute_list: str, key: str, value: str) -> Dict:
    """Filters out the the attributes by key-value matching in the ISA JSON

    Args:
        element (str): _description_
        key (str): _description_
        value (str): _description_

    Example:
    my_element = {"comments": [
        { "name": "SEEK Study ID", "value": "2" },
        { "name": "SEEK creation date", "value": "2023-09-22T06:14:34Z" }
      ]
    }
    filter_attribute_by(element = my_element, key = 'name', value= 'SEEK Study ID')

    Output: { "name": "SEEK Study ID", "value": "2" }

    Returns:
        Dict: The Dict that matches the criteria
    """
    return [attribute for attribute in attribute_list if attribute[key] == value]


def validate_dict(dict: Dict, key: str) -> None:
    """Raises an error if the structure of the ISA JSON Dict is not conform

    Args:
        isa_json (Dict): The ISA JSON to validate
        key (str): The key to check

    Raises:
        KeyError: Will display the missing key in the Dict
    """
    if key not in dict.keys():
        raise KeyError(f"{key} was not found in the provided ISA JSON.")


def get_assay_sample_associations(assay_dict: Dict):
    process_sequence = []
    for process in assay_dict["processSequence"]:
        input_ids = [input["@id"] for input in process["inputs"]]
        output_ids = [output["@id"] for output in process["outputs"]]
        process_sequence.append({"input": input_ids, "output": output_ids})

    return process_sequence
