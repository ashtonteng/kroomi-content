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
