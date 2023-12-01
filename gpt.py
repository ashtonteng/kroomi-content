from typing import List, Tuple
import time
import requests
import os


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
        model="gpt-4-1106-preview",
        temperature=0.3,
    )
    return chat_completion.choices[0].message.content


# TODO: currently deprecated due to poor performance
def assistant_extract_protocol(client, chunks: List[str]) -> str:
    responses = []
    extractor_prompt = open('prompts/extractor.txt', 'r').read()
    # file = client.files.create(
    #     file=open('...', 'rb'),
    #     purpose="assistants",
    # )
    assistant = client.beta.assistants.create(
        name="Video Transcript Health Actions Extractor",
        instructions=extractor_prompt,
        # tools=[{"type": "retrieval"}],
        # file_ids=[file.id],
        model="gpt-4-1106-preview",
    )
    thread = client.beta.threads.create()

    # TODO: parallelize this
    for chunk in chunks:
        _ = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=chunk,
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            # instructions=extractor_prompt,
        )
        while run.status != 'completed':
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(run.status)
            time.sleep(5)
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        responses.append(messages.data[0].content[0].text.value)
    return '\n'.join(responses)


def assistant_timestamp_finder(client,
                               filepath: str,
                               actions: List[str]) -> Tuple[str, List[str]]:
    responses = []
    prompt = open('prompts/timestamp_finder.txt', 'r').read()
    file = client.files.create(
        file=open(filepath, 'rb'),
        purpose="assistants",
    )
    assistant = client.beta.assistants.create(
        name="Video Transcript Timestamp Finder",
        instructions=prompt,
        tools=[{"type": "retrieval"}],
        file_ids=[file.id],
        model="gpt-4-1106-preview",
    )
    thread = client.beta.threads.create()
    for action in actions:
        if action.strip() == '':
            continue
        _ = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=action,
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            # instructions=extractor_prompt,
        )
        while run.status != 'completed':
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(run.status)
            time.sleep(5)
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        response = messages.data[0].content[0].text.value
        print(action, response)
        responses.append(response)
    delete_assistant(assistant.id)
    return assistant.id, responses


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
        model="gpt-4-1106-preview",
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
        model="gpt-4-1106-preview",
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

