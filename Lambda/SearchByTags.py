import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME  = 'ImageLabels'

def lambda_handler(event, context):
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']
    query = body['query']
    tag_requirements = parse_query(query)
    
    response = dynamodb.scan(TableName=DB_NAME)
    items = response['Items']
    
    results = []
    for item in items:
        try:
            item_tags_str = item['Tags']['S']
            item_tags = json.loads(item_tags_str)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for item {item['ImageKey']['S']}: {e}")
            continue
        
        if check_tag_requirements(item_tags, tag_requirements):
            results.append({
                'thumbnail': item['ThumbnailURL']['S'],
                'fullsize': item['S3ImageURL']['S']
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps({'links': results}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def parse_query(query):
    tags = query.split(', ')
    tag_requirements = {}
    for tag_count in tags:
        tag, count = tag_count.split(': ')
        tag_requirements[tag.strip()] = int(count.strip())
    return tag_requirements


def check_tag_requirements(item_tags, tag_requirements):
    tag_counts = {tag: item_tags.count(tag) for tag in tag_requirements}
    for tag, required_count in tag_requirements.items():
        if tag_counts.get(tag, 0) < required_count:
            return False
    return True
