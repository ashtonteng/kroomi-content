import os

TRANSCRIPTS_DIR = '0_transcripts'
TRANSCRIPTS_NO_TIMESTAMPS_DIR = '0_transcripts_no_timestamps'
EXTRACTED_NO_TIMESTAMPS_DIR = '1_extracted_no_timestamps'
TIMESTAMPS_ADDED_DIR = '2_timestamps_added'
FORMATTED_DIR = '3_formatted'
FINAL_JSON_DIR = '4_final_json'


def get_saved_file_if_exists(dirname: str, filename: str) -> str:
    """
    :param dirname: directory to look in
    :param filename: filename to look for
    :return: the file contents if it exists, otherwise None
    """
    if os.path.exists(f'{dirname}/{filename}.txt'):
        return open(f'{dirname}/{filename}.txt', 'r').read()
    else:
        return None


def write_saved_file(dirname: str, filename: str, contents: str) -> None:
    """
    :param dirname: directory to write to
    :param filename: filename to write to
    :param contents: contents to write
    :return: None
    """
    with open(f'{dirname}/{filename}.txt', 'w') as f:
        f.write(contents)

