from dotenv import load_dotenv
from youtube import *
from util import *
from gpt import *
from protocol import *
import openai

VIDEO_ASSISTANT_ID_MAP_FILE = 'video_assistant_id_map.tsv'


def youtube_url_to_json(openai_client: openai.Client,
                        youtube_url: str,
                        extractor: bool = True,
                        timestamper: bool = False,
                        formatter: bool = True,
                        output_json: bool = True) -> None:
    video_id = extract_youtube_video_id(youtube_url)
    metadata = get_metadata_youtube_video(video_id)
    title = metadata['title']
    channel = metadata['channel']
    description = metadata['description']
    description_first_paragraph = metadata['description_first_paragraph']
    rewrite = False

    if not os.path.exists(f'0_transcripts/{video_id}.txt'):
        print("downloading transcript with timestamps for video:", video_id, title)
        response = get_transcript_from_youtube_video(video_id, timestamps=True, description=description)
        with open(f'0_transcripts/{video_id}.txt', 'w') as f:
            f.write(response)

    if os.path.exists(f'0_transcripts_no_timestamps/{video_id}.txt'):
        response = open(f'0_transcripts_no_timestamps/{video_id}.txt', 'r').read()
    else:
        print("downloading transcript without timestamps for video:", video_id, title)
        response = get_transcript_from_youtube_video(video_id, timestamps=False, description=description)
        with open(f'0_transcripts_no_timestamps/{video_id}.txt', 'w') as f:
            f.write(response)
        rewrite = True

    if extractor:
        if os.path.exists(f'1_extracted_no_timestamps/{video_id}.txt') and not rewrite:
            response = open(f'1_extracted_no_timestamps/{video_id}.txt', 'r').read()
        else:
            print("extracting protocol for video:", video_id, title)
            response = extract_protocol(openai_client, response)
            with open(f'1_extracted_no_timestamps/{video_id}.txt', 'w') as f:
                f.write(response)
            rewrite = True

    if timestamper:
        if os.path.exists(f'2_timestamps_added/{video_id}.txt') and not rewrite:
            response = open(f'2_timestamps_added/{video_id}.txt', 'r').read()
        else:
            print("getting timestamps for video:", video_id, title)
            # for each of the protocol actions, query assistant for the timestamp
            actions = response.split('\n')
            assistant_id, timestamps = assistant_timestamp_finder(client, f'0_transcripts/{video_id}.txt', actions)
            with open(VIDEO_ASSISTANT_ID_MAP_FILE, 'a') as f:
                f.write(f"{title}\t{video_id}\t{assistant_id}\n")
            print("video_id", video_id, "assistant_id", assistant_id)
            print(timestamps)
            if len(timestamps) != len(actions):
                raise Exception('Number of timestamps does not match number of chunks')
            for i in range(len(actions)):
                actions[i] = f"{actions[i]} ({timestamps[i]})"
            response = '\n'.join(actions)
            with open(f'2_timestamps_added/{video_id}.txt', 'w') as f:
                f.write(response)

    if formatter:
        if os.path.exists(f'3_formatted/{video_id}.json') and not rewrite:
            response = open(f'3_formatted/{video_id}.json', 'r').read()
        else:
            print("formatting protocol for video:", video_id, title)
            response = format_protocol(openai_client, response)
            with open(f'3_formatted/{video_id}.json', 'w') as f:
                f.write(response)
            rewrite = True

    if output_json:
        if os.path.exists(f'4_final_json/{video_id}.json') and not rewrite:
            return
        formatted_protocol_actions_json = json.loads(response)
        if 'protocol_actions' not in formatted_protocol_actions_json:
            raise Exception('No protocol actions found')
        protocol = Protocol(title, channel, description_first_paragraph, video_id)
        protocol.add_protocol_actions(
            formatted_protocol_actions_json['protocol_actions']
        )
        formatted_json = protocol.to_json()
        print("writing final json for video:", video_id, title)
        with open(f'4_final_json/{video_id}.json', 'w') as f:
            f.write(formatted_json)


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

    # url = input("Enter youtube url: ")
    # youtube_url_to_json(openai_client, url)

    seed_urls = open('seed_urls.txt', 'r').readlines()
    for seed_url in seed_urls:
        url = seed_url.strip()
        youtube_url_to_json(client, url,
                            extractor=True,
                            timestamper=True,
                            formatter=True,
                            output_json=True)
