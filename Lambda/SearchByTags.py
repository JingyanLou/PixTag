import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME  = 'ImageLabels'

def lambda_handler(event, context):
    # Parsing tags sent by clients 
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']
    query        = body['query']
    quested_tags = parse_query(query)
    
    # Retriving all items from DynamoDB
    response = dynamodb.scan(TableName = DB_NAME)
    items    = response['Items']
    
    results  = []  
    for item in items:
        item_tags     = json.loads(item['Tags']['S'])    
        # Store both thumbnail and full image URLs.
        if check_tag_requirements(item_tags, quested_tags):
            results.append({
                'fullsize' :   item['S3ImageURL']['S'],
                'thumbnail': item['ThumbnailURL']['S']
            })
    return {
        'statusCode': 200,
        'body': json.dumps({'links': results}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

# Parsing query and stored 'em in a dictionary 
# Such as  {tag_1: count_1, tag_2: count_2...}
def parse_query(query):
    tags = query.split(', ')
    quested_tags  = {}
    for tag_count in tags:
        tag, count= tag_count.split(': ')
        quested_tags[tag.strip()] = int(count.strip())
    return quested_tags


# Validating if current item have all tags by required amount 
def check_tag_requirements(item_tags, quested_tags):
    tag_counts = {tag: item_tags.count(tag) 
                   for tag in quested_tags}
        
    for tag, required_count in quested_tags.items():
        if  tag_counts.get(tag, 0) < required_count:
            return False
    return True
