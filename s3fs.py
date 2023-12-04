import boto3
import logging

BUCKET_NAME = "kroomi-content"
TRANSCRIPTS_DIR = '0_transcripts'
TRANSCRIPTS_NO_TIMESTAMPS_DIR = '0_transcripts_no_timestamps'
EXTRACTED_NO_TIMESTAMPS_DIR = '1_extracted_no_timestamps'
TIMESTAMPS_ADDED_DIR = '2_timestamps_added'
FORMATTED_DIR = '3_formatted'
FINAL_JSON_DIR = '4_final_json'

# TODO: make file system a class


def get_saved_file_if_exists(dirname: str, filename: str) -> str:
    """
    :param dirname: directory to look in
    :param filename: filename to look for
    :return: the file contents if it exists, otherwise None
    """
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=f'{dirname}/{filename}.txt')
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        logging.error(f"could not get file {filename} from s3: {e}")
        return None


def write_saved_file(dirname: str, filename: str, contents: str) -> None:
    """
    :param dirname: directory to write to
    :param filename: filename to write to
    :param contents: contents to write
    :return: None
    """
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=f'{dirname}/{filename}.txt', Body=contents)
    except Exception as e:
        logging.error(f"could not write file {filename} to s3: {e}")


