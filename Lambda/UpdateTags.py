import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME  = 'ImageLabels'
def lambda_handler(event, context):
    body = json.loads(event['body'])
    urls = body['url']
    action_type = body['type']
    tags = body['tags']
    
    for url in urls:
        response = dynamodb.scan(
            TableName = DB_NAME,
            FilterExpression='ThumbnailURL = :val',
            ExpressionAttributeValues={':val': {'S': url}}
        )
        
        items = response['Items']
        if not items:
            continue
        
        item = items[0]
        current_tags = json.loads(item['Tags']['S'])
        
        if action_type == 1:  # Add tags
            for tag in tags:
                current_tags.append(tag)
        elif action_type == 0:  # Remove tags
            current_tags = [tag for tag in current_tags if tag not in tags]
        
        dynamodb.update_item(
            TableName = DB_NAME,
            Key={'ImageKey': item['ImageKey']},
            UpdateExpression='SET Tags = :val',
            ExpressionAttributeValues={':val': {'S': json.dumps(current_tags)}}
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tags updated successfully'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
