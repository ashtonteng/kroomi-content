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
    filepath = f'{dirname}/{filename}.txt'

    # Check if the file exists in the S3 bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=filepath)

    # If 'Contents' key is in the response and it's not empty, the file exists
    if 'Contents' in response and len(response['Contents']) > 0:
        # File exists, retrieve it
        file_object = s3.get_object(Bucket=BUCKET_NAME, Key=filepath)
        file_content = file_object['Body'].read().decode('utf-8')
        return file_content
    else:
        # File does not exist
        print(f"{filepath} does not exist, creating...")
        return ""


def write_saved_file(dirname: str, filename: str, contents: str) -> None:
    """
    :param dirname: directory to write to
    :param filename: filename to write to
    :param contents: contents to write
    :return: None
    """
    s3 = boto3.client('s3')
    filepath = f'{dirname}/{filename}.txt'
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=filepath, Body=contents)
    except Exception as e:
        logging.error(f"could not write file {filepath} to s3: {e}")
        raise e


