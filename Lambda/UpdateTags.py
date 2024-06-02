import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME = 'ImageLabels'

def lambda_handler(event, context):
    print('Received event:', json.dumps(event))
    
    if 'body' in event:
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        else:
            body = body
    else:
        body = event  # In case the event is already a dictionary and not string-encoded
    
    print('Parsed body:', json.dumps(body))
    
    urls = body['url']
    action_type = body['type']
    tags = body['tags']
    
    for url in urls:
        response = dynamodb.scan(
            TableName=DB_NAME,
            FilterExpression='ThumbnailURL = :val',
            ExpressionAttributeValues={':val': {'S': url}}
        )
        
        items = response['Items']
        if not items:
            print(f"No items found for URL: {url}")
            continue
        
        item = items[0]
        current_tags = json.loads(item['Tags']['S'])
        
        if action_type == 1:  # Add tags
            for tag in tags:
                current_tags.append(tag)
        elif action_type == 0:  # Remove tags
            current_tags = [tag for tag in current_tags if tag not in tags]
        
        dynamodb.update_item(
            TableName=DB_NAME,
            Key={'ImageKey': {'S': item['ImageKey']['S']}},
            UpdateExpression='SET Tags = :val',
            ExpressionAttributeValues={':val': {'S': json.dumps(current_tags)}}
        )
    
    response = {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tags updated successfully'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    
    print('Response:', json.dumps(response))
    
    return response
