from dotenv import load_dotenv
from youtube import *
from util import *
from gpt import *
from protocol import *
import openai
import concurrent.futures
import localfs
import s3fs

VIDEO_ASSISTANT_ID_MAP_FILE = 'video_assistant_id_map.tsv'


def youtube_url_to_json_local(
        openai_client: openai.Client,
        youtube_url: str,
        file_system: str = 'local',
        extractor: bool = True,
        timestamper: bool = True,
        formatter: bool = True,
        output_json: bool = True) -> None:
    video_id = extract_youtube_video_id(youtube_url)
    metadata = get_metadata_youtube_video(video_id)
    title = metadata['title']
    channel = metadata['channel']
    description = metadata['description']
    description_first_paragraph = metadata['description_first_paragraph']
    rewrite = False

    if file_system == 'local':
        fs = localfs
    else:
        fs = s3fs

    transcript_with_timestamps = fs.get_saved_file_if_exists(fs.LOCAL_TRANSCRIPTS_DIR, video_id)
    if not transcript_with_timestamps:
        print(f"getting transcript for video {video_id}: {title}")
        transcript_with_timestamps = get_transcript_from_youtube_video(video_id, timestamps=True, description=description)
        fs.write_saved_file(fs.LOCAL_TRANSCRIPTS_DIR, video_id, transcript_with_timestamps)
        rewrite = True

    transcript_without_timestamps = fs.get_saved_file_if_exists(fs.LOCAL_TRANSCRIPTS_NO_TIMESTAMPS_DIR, video_id)
    if not transcript_without_timestamps:
        print(f"getting transcript without timestamps for video {video_id}: {title}")
        transcript_without_timestamps = get_transcript_from_youtube_video(video_id, timestamps=False, description=description)
        fs.write_saved_file(fs.LOCAL_TRANSCRIPTS_NO_TIMESTAMPS_DIR, video_id, transcript_without_timestamps)
        rewrite = True

    if not extractor:
        return

    extracted_protocol = fs.get_saved_file_if_exists(fs.LOCAL_EXTRACTED_NO_TIMESTAMPS_DIR, video_id)
    # if we don't have the extracted protocol, or we want to rewrite it, extract it
    if not extracted_protocol or rewrite:
        print(f"extracting protocol for video {video_id}: {title}")
        extracted_protocol = extract_protocol(openai_client, transcript_without_timestamps)
        fs.write_saved_file(fs.LOCAL_EXTRACTED_NO_TIMESTAMPS_DIR, video_id, extracted_protocol)
        rewrite = True

    if not timestamper:
        return

    timestamped_protocol = fs.get_saved_file_if_exists(fs.LOCAL_TIMESTAMPS_ADDED_DIR, video_id)
    if not timestamped_protocol or rewrite:
        print(f"getting timestamps for video {video_id}: {title}")
        # for each of the protocol actions, query assistant for the timestamp
        actions = extracted_protocol.split('\n')
        # make sure to get rid of empty bullet points in actions
        actions = [action for action in actions if action.strip() != '']
        assistant_id, timestamps = assistant_timestamp_finder(client, transcript_with_timestamps, actions)
        with open(VIDEO_ASSISTANT_ID_MAP_FILE, 'a') as f:
            f.write(f"{title}\t{video_id}\t{assistant_id}\n")
        if len(timestamps) != len(actions):
            raise Exception('Number of timestamps does not match number of chunks')
        for i in range(len(actions)):
            actions[i] = f"{actions[i]} {timestamps[i]}"
        timestamped_protocol = '\n'.join(actions)
        fs.write_saved_file(fs.LOCAL_TIMESTAMPS_ADDED_DIR, video_id, timestamped_protocol)

    if not formatter:
        return

    formatted_protocol = fs.get_saved_file_if_exists(fs.LOCAL_FORMATTED_DIR, video_id)
    if not formatted_protocol or rewrite:
        print(f"formatting protocol for video {video_id}: {title}")
        formatted_protocol = format_protocol(openai_client, timestamped_protocol)
        fs.write_saved_file(fs.LOCAL_FORMATTED_DIR, video_id, formatted_protocol)
        rewrite = True

    if not output_json:
        return

    formatted_json = fs.get_saved_file_if_exists(fs.LOCAL_FINAL_JSON_DIR, video_id)
    if not formatted_json or rewrite:
        formatted_protocol_actions_json = json.loads(formatted_protocol)
        if 'protocol_actions' not in formatted_protocol_actions_json:
            raise Exception('No protocol actions found')
        protocol = Protocol(title, channel, description_first_paragraph, video_id)
        protocol.add_protocol_actions(
            formatted_protocol_actions_json['protocol_actions']
        )
        formatted_json = protocol.to_json()
        print("writing final json for video:", video_id, title)
        fs.write_saved_file(fs.LOCAL_FINAL_JSON_DIR, video_id, formatted_json)


if __name__ == "__main__":
    load_dotenv()
    client = openai.Client()
    directories_to_create = [
        '0_transcripts',
        '0_transcripts_no_timestamps',
        '1_extracted_no_timestamps',
        '3_formatted',
        '4_final_json'
    ]
    for directory in directories_to_create:
        if not os.path.exists(directory):
            os.makedirs(directory)

    def extract_one_url(url):
        youtube_url_to_json_local(client, url,
                            extractor=True,
                            timestamper=True,
                            formatter=True,
                            output_json=True)


    def extract_seed_urls():
        seed_urls = open('seed_urls.txt', 'r').readlines()
        for seed_url in seed_urls:
            url = seed_url.strip()
            youtube_url_to_json_local(client, url,
                                extractor=True,
                                timestamper=True,
                                formatter=True,
                                output_json=True)

    def parallel_extract_seed_urls(max_threads: int = 5):
        seed_urls = open('seed_urls.txt', 'r').readlines()
        seed_urls = [url.strip() for url in seed_urls]
        seed_urls = list(set(seed_urls))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit tasks to the executor
            futures = [executor.submit(extract_one_url, url) for url in seed_urls]
            # Wait for all futures to complete (optional, if you need to process results)
            for future in concurrent.futures.as_completed(futures):
                # Handle exceptions or get results here if needed
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred: {e}")

    parallel_extract_seed_urls(5)
