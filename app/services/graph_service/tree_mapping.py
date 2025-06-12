import json
from typing import Dict, List, Union

# 너가 준 원본 JSON (여기서는 일부만 복사해옴, 실제로는 전체 넣어야 함)
original_json = {
    "results": {
        "root": "machine learning",
        "children": [
            {
                "id": "cooperative regenerating code",
                "value": 1.0,
                "sim": 0.5559,
                "children": [
                    {"id": "cooperative regenerating code", "value": 0.8, "pids": [...]},
                    {"id": "cooperative regenerating", "value": 0.1874, "pids": [...]},
                    {"id": "minimum storage", "value": -0.2833, "pids": [...]}
                ]
            },
            ...
        ]
    }
}

# TreeMapping 타입 정의
TreeMapping = Dict[
    str,
    Dict[
        str,
        Union[
            float,
            str,
            List[Dict[str, Union[str, float, str]]]
        ]
    ]
]

# JSON → TreeMapping
def extract_tree_mapping(data: dict) -> (str, TreeMapping):
    root = data["results"]["root"]
    mapping = {}

    for child in data["results"]["children"]:
        mapping[child["id"]] = {
            "value": child["value"],
            "children": child["children"]
        }

    return root, mapping
