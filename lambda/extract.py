def extract_protocol_youtube_url(event, context):
    user = event['user']
    type = event['type']
    content = event['content']
    if type != "youtube":
        return {
            "statusCode": 400,
            "body": "Invalid type"
        }
    url = content

    return {
        "statusCode": 200,
        "body": "Hello from AWS Lambda using SAM!"
    }
