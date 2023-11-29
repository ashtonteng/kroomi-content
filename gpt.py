from typing import List
import time


def extract_protocol(client, text: str) -> str:
    extractor_prompt = open('prompts/extractor.txt', 'r').read()
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
