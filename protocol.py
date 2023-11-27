from typing import List, Dict
import json


class Protocol:
    def __init__(self, name: str, author: str, description: str,
                 video_id: str):
        self.name = name
        self.author = author
        self.description = description
        self.video_id = video_id
        self.protocol_actions = []

    def add_protocol_actions(self, protocol_actions: List[Dict[str, str]]):
        for protocol_action in protocol_actions:
            formatted_timestamp = f"https://youtu.be/{self.video_id}?t={str(protocol_action['source_timestamp'])}s"
            self.protocol_actions.append(
                {
                    'name': protocol_action['name'],
                    'description': protocol_action['description'],
                    'category': protocol_action['category'],
                    'source_timestamp': formatted_timestamp,
                 }
            )

    def to_dict(self):
        return {
            "protocols": [
                {
                    "name": self.name,
                    "author": self.author,
                    "description": self.description,
                    "source": f"https://youtu.be/{self.video_id}",
                    "protocol_actions": self.protocol_actions
                }
            ],
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

