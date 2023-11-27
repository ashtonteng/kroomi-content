from dotenv import load_dotenv
from youtube import *
from util import *
from gpt import *
import openai


def youtube_url_to_json(openai_client, url: str) -> str:
    video_id = extract_youtube_video_id(url)
    print("getting transcript for video id: ", video_id)
    transcript = get_transcript_from_youtube_video(video_id)
    with open(f'0_transcripts/{video_id}.txt', 'w') as f:
        f.write(transcript)

    print("extracting protocol for video id: ", video_id)
    extracted_protocol = extract_protocol(openai_client, transcript)
    with open(f'1_extracted/{video_id}.txt', 'w') as f:
        f.write(extracted_protocol)

    print("refining protocol for video id: ", video_id)
    # extracted_protocol = open(f'1_extracted/{video_id}.txt', 'r').read()
    refined_protocol = refine_protocol(openai_client, extracted_protocol)
    with open(f'2_refined/{video_id}.txt', 'w') as f:
        f.write(refined_protocol)

    print("formatting protocol for video id: ", video_id)
    # refined_protocol = open(f'2_refined/{video_id}.txt', 'r').read()
    formatted_protocol = format_protocol(openai_client, refined_protocol)
    with open(f'3_formatted/{video_id}.json', 'w') as f:
        f.write(formatted_protocol)

    print("getting metadata for video id: ", video_id)
    # formatted_protocol = open(f'3_formatted/{video_id}.json', 'r').read()
    formatted_protocol_json = json.loads(formatted_protocol)
    metadata = get_metadata_youtube_video(video_id)
    formatted_json = format_protocol_json(metadata['title'],
                                          metadata['channel'],
                                          metadata['description'],
                                          url,
                                          formatted_protocol_json[
                                              'protocol_actions'])

    print(f"writing final json for video id: {video_id}, "
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

    url = input("Enter youtube url: ")
    youtube_url_to_json(openai_client, url)

    # seed_urls = open('seed_urls.txt', 'r').readlines()
    # print(seed_urls)
    # for seed_url in seed_urls:
    #     url = seed_url.strip()
    #     youtube_url_to_json(openai_client, url)
