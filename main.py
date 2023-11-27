from dotenv import load_dotenv
from youtube import *
from util import *
from gpt import *
from protocol import *
import openai


def youtube_url_to_json(openai_client, url: str) -> str:
    video_id = extract_youtube_video_id(url)
    metadata = get_metadata_youtube_video(video_id)
    title = metadata['title']
    channel = metadata['channel']
    description = metadata['description']

    if os.path.exists(f'0_transcripts/{video_id}.txt'):
        print("loading transcript for video:", video_id)
        transcript = open(f'0_transcripts/{video_id}.txt', 'r').read()
    else:
        print("downloading transcript for video:", video_id)
        transcript = get_transcript_from_youtube_video(video_id)
        with open(f'0_transcripts/{video_id}.txt', 'w') as f:
            f.write(transcript)

    if os.path.exists(f'1_extracted/{video_id}.txt'):
        print("loading extracted protocol for video:", video_id)
        extracted_protocol = open(f'1_extracted/{video_id}.txt', 'r').read()
    else:
        print("extracting protocol for video:", video_id)
        extracted_protocol = extract_protocol(openai_client, transcript)
        with open(f'1_extracted/{video_id}.txt', 'w') as f:
            f.write(extracted_protocol)

    # print("refining protocol for video id: ", video_id)
    # # extracted_protocol = open(f'1_extracted/{video_id}.txt', 'r').read()
    # refined_protocol = refine_protocol(openai_client, extracted_protocol)
    # with open(f'2_refined/{video_id}.txt', 'w') as f:
    #     f.write(refined_protocol)

    if os.path.exists(f'3_formatted/{video_id}.json'):
        print("loading formatted protocol for video:", video_id)
        formatted_protocol = open(f'3_formatted/{video_id}.json', 'r').read()
    else:
        print("formatting protocol for video:", video_id)
        formatted_protocol = format_protocol(openai_client, extracted_protocol)
        with open(f'3_formatted/{video_id}.json', 'w') as f:
            f.write(formatted_protocol)

    formatted_protocol_actions_json = json.loads(formatted_protocol)
    if 'protocol_actions' not in formatted_protocol_actions_json:
        raise Exception('No protocol actions found')
    protocol = Protocol(title, channel, description, video_id)
    protocol.add_protocol_actions(formatted_protocol_actions_json['protocol_actions'])
    formatted_json = protocol.to_json()

    print(f"writing final json for video: {video_id}, "
          f"{metadata['title']}")
    with open(f'4_final_json/{video_id}.json', 'w') as f:
        f.write(formatted_json)


if __name__ == "__main__":
    load_dotenv()
    openai_client = openai.Client()

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
        youtube_url_to_json(openai_client, url)
