import json
import boto3

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb')
DB_NAME = 'ImageLabels'

def lambda_handler(event, context):
    try:
        # Parse the request body
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
            else:
                body = body
        else:
            body = event  # In case the event is already a dictionary and not string-encoded

        # Extract the query and username from the request body
        query = body['query']
        username = body.get('username')

        # Check if query and username are provided
        if not query or not username:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Query and username are required'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

        # Parse the query to get tag requirements
        tag_requirements = parse_query(query)

        # Scan the DynamoDB table for items belonging to the specified user
        response = dynamodb.scan(
            TableName=DB_NAME,
            FilterExpression='UserName = :username',
            ExpressionAttributeValues={':username': {'S': username}}
        )
        items = response['Items']

        results = []
        for item in items:
            try:
                # Extract and parse the tags from the item
                item_tags_str = item['Tags']['S']
                item_tags = json.loads(item_tags_str)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for item {item['ImageKey']['S']}: {e}")
                continue

            # Check if the item's tags meet the tag requirements
            if check_tag_requirements(item_tags, tag_requirements):
                results.append({
                    'thumbnail': item['ThumbnailURL']['S'],
                    'fullsize': item['S3ImageURL']['S']
                })

        # Return the search results
        return {
            'statusCode': 200,
            'body': json.dumps({'links': results}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except json.JSONDecodeError:
        # Handle JSON decoding errors
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON format'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as e:
        # Handle any other exceptions
        print(f"Unhandled exception: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

def parse_query(query):
    """
    Parse the query string into a dictionary of tag requirements.
    Example input: "person: 2, car: 1"
    Example output: {"person": 2, "car": 1}
    """
    tags = query.split(', ')
    tag_requirements = {}
    for tag_count in tags:
        tag, count = tag_count.split(': ')
        tag_requirements[tag.strip()] = int(count.strip())
    return tag_requirements

def check_tag_requirements(item_tags, tag_requirements):
    """
    Check if the item's tags meet the tag requirements.
    Example:
        item_tags = ["person", "car", "car"]
        tag_requirements = {"person": 1, "car": 2}
        return True
    """
    tag_counts = {tag: item_tags.count(tag) for tag in tag_requirements}
    for tag, required_count in tag_requirements.items():
        if tag_counts.get(tag, 0) < required_count:
            return False
    return True
