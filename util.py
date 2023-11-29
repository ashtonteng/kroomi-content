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


def get_text_chunks(text: str, delimiter: str,
                    num_delimiters_per_chunk: int,
                    num_delimiters_overlap_between_chunks: int) -> List[str]:
    """
    Breaks down a string into chunks of text, delimited by a certain character.

    :param text: the input text
    :param delimiter: the delimiter used to split the text into chunks
    :param num_delimiters_per_chunk: the number of delimiters per chunk
    :param num_delimiters_overlap_between_chunks: the number of delimiters to overlap between chunks
    :return: a list of text chunks
    """
    text_chunks = []
    text_split = text.split(delimiter)
    for i in range(0, len(text_split), num_delimiters_per_chunk):
        text_chunk = delimiter.join(
            text_split[i:i + num_delimiters_per_chunk + num_delimiters_overlap_between_chunks])
        text_chunks.append(text_chunk)
    return text_chunks
