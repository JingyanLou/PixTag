import json
import boto3

DB_NAME  = 'ImageLabels'
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    # Retrieves queries information
    urls         = body[ 'url']
    quested_tags = body['tags']
    actions_type = body['type']
    
    # Process url by url accordingly 
    for url in urls:
        response = dynamodb.scan(
            TableName                = DB_NAME,
            FilterExpression         = 'ThumbnailURL = :val',
            ExpressionAttributeValues= {':val': {'S': url}}
        )
        
        items = response['Items']
        if not items:
            continue
        
        item      = items[0]
        curr_tags = json.loads(item['Tags']['S'])
        
        # Adding tags or removing based on action type 
        if actions_type   == 1:  
            for tag in quested_tags:
                curr_tags.append(tag)
        elif actions_type == 0:  
            curr_tags = [tag for tag in curr_tags if tag not in quested_tags]
        
        # Updates DynamoDB with new tags provided 
        dynamodb.update_item(
            TableName = DB_NAME,
            Key       = {'ImageKey': item['ImageKey']},
            UpdateExpression          = 'SET Tags = :val',
            ExpressionAttributeValues = {':val': {'S': json.dumps(curr_tags)}}
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Tags updated successfully'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
