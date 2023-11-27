from dotenv import load_dotenv
from youtube import *
from util import *
from gpt import *
from protocol import *
import openai


def youtube_url_to_json(openai_client: openai.Client,
                        youtube_url: str,
                        extractor: bool = True,
                        refiner: bool = False,
                        formatter: bool = True,
                        output_json: bool = True) -> None:
    video_id = extract_youtube_video_id(youtube_url)
    metadata = get_metadata_youtube_video(video_id)
    title = metadata['title']
    channel = metadata['channel']
    description = metadata['description']
    rewrite = False

    if os.path.exists(f'0_transcripts/{video_id}.txt'):
        response = open(f'0_transcripts/{video_id}.txt', 'r').read()
    else:
        print("downloading transcript for video:", video_id, title)
        response = get_transcript_from_youtube_video(video_id)
        with open(f'0_transcripts/{video_id}.txt', 'w') as f:
            f.write(response)
        rewrite = True

    if extractor:
        if os.path.exists(f'1_extracted/{video_id}.txt') and not rewrite:
            response = open(f'1_extracted/{video_id}.txt', 'r').read()
        else:
            print("extracting protocol for video:", video_id, title)
            response = extract_protocol(openai_client, response)
            with open(f'1_extracted/{video_id}.txt', 'w') as f:
                f.write(response)
            rewrite = True

    if refiner:
        if os.path.exists(f'2_refined/{video_id}.txt') and not rewrite:
            response = open(f'2_refined/{video_id}.txt', 'r').read()
        else:
            print("refining protocol for video id: ", video_id, title)
            response = refine_protocol(openai_client, response)
            with open(f'2_refined/{video_id}.txt', 'w') as f:
                f.write(response)
            rewrite = True

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
        protocol = Protocol(title, channel, description, video_id)
        protocol.add_protocol_actions(formatted_protocol_actions_json['protocol_actions'])
        formatted_json = protocol.to_json()
        print("writing final json for video:", video_id, title)
        with open(f'4_final_json/{video_id}.json', 'w') as f:
            f.write(formatted_json)


if __name__ == "__main__":
    load_dotenv()
    client = openai.Client()
    directories_to_create = [
        '0_transcripts',
        '1_extracted',
        '2_refined',
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
        youtube_url_to_json(client, url)
