from typing import Dict, List
import json


# TODO: format multiple protocols into the same JSON
def format_protocol_json(name: str, author: str, description: str, source: str,
                         protocol_actions: List[Dict[str, str]]) -> str:
    formatted_json = json.dumps(
        {
            "protocols": [
                {
                    "name": name,
                    "author": author,
                    "description": description,
                    "source": source,
                    "protocol_actions": protocol_actions
                }
            ],
        },
        indent=4,
    )
    return formatted_json
