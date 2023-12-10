from typing import List, Tuple
import time
import logging
import tempfile
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

MODEL = "gpt-4-1106-preview" #"gpt-3.5-turbo-1106"
# logging.basicConfig(level=logging.INFO)


def extract_protocol(client, text: str) -> str:
    extractor_prompt = open('prompts/extractor_no_timestamp.txt', 'r').read()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": extractor_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model=MODEL,
        temperature=0.3,
    )
    return chat_completion.choices[0].message.content


def get_timestamp_for_action(client, assistant_id, action) -> str:
    """
    the timestamp returned is a string in the format (seconds).
    """
    logger = logging.getLogger("gpt")
    try:
        thread = client.beta.threads.create()
        _ = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=action,
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        while run.status != 'completed':
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            time.sleep(5)
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        response = messages.data[0].content[0].text.value
        logger.info(f"{action} {response}")
        print(f"{action} {response}")
        return response
    except Exception as e:
        logger.error(f"could not get timestamp for action {action}: {e}")
        # return a timestamp of 0 if there is an error, this is not critical
        return "(0)"


def assistant_timestamp_finder(client,
                               transcript_with_timestamps: str,
                               actions: List[str],
                               parallel: bool = True) -> Tuple[str, List[str]]:
    logger = logging.getLogger("gpt")

    # first make a temporary file from the transcript for upload
    with tempfile.NamedTemporaryFile(mode='w', suffix=".txt", delete=False) as f:
        f.write(transcript_with_timestamps)
        temp_transcript_filepath = f.name

    prompt = open('prompts/timestamp_finder.txt', 'r').read()
    file = client.files.create(
        file=open(temp_transcript_filepath, 'rb'),
        purpose="assistants",
    )
    assistant = client.beta.assistants.create(
        name="Video Transcript Timestamp Finder",
        instructions=prompt,
        tools=[{"type": "retrieval"}],
        file_ids=[file.id],
        model=MODEL,
    )

    logger.info(f"created assistant {assistant.id} for timestamp finding")

    if parallel:
        # Initialize a dictionary to store results
        results_dict = {}
        with ThreadPoolExecutor(max_workers=len(actions)) as executor:
            # Submit tasks
            future_to_index = {executor.submit(get_timestamp_for_action, client,
                                               assistant.id, action): i for i, action in enumerate(actions)}
            # Retrieve results as they are completed
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                result = future.result()
                logger.info(f"got result for action {index} {actions[index]}: {result}")
                results_dict[index] = result
        # Order results based on the original actions list
        timestamps = [results_dict[i] for i in range(len(actions))]
    else:
        timestamps = []
        for action in actions:
            timestamp = get_timestamp_for_action(client, assistant.id, action)
            timestamps.append(timestamp)

    # clean up file and assistant
    os.remove(temp_transcript_filepath)
    delete_assistant(assistant.id)
    return assistant.id, timestamps


def refine_protocol(client, text: str) -> str:
    refiner_prompt = open('prompts/refiner.txt', 'r').read()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": refiner_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model=MODEL,
        temperature=0.0,
    )
    return chat_completion.choices[0].message.content


def format_protocol(client, text: str) -> str:
    formatter_prompt = open('prompts/formatter.txt', 'r').read()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": formatter_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model=MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return chat_completion.choices[0].message.content


def delete_assistant(assistant_id: str) -> None:
    api_key = os.getenv('OPENAI_API_KEY')
    url = f'https://api.openai.com/v1/assistants/{assistant_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'OpenAI-Beta': 'assistants=v1'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code != 200:
        raise Exception('Delete assistant failed')

