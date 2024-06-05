import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME  = 'ImageLabels'

def lambda_handler(event, context):
    print('Received event:', json.dumps(event))
    # Retrieves inputs from user
    if 'body' in event:
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        else:
            body = body
    else:
        body = event  
        # In case the event is already a dictionary and not string-encoded
    print('Parsed body:', json.dumps(body))
    
    urls        = body ['url']
    action_type = body['type']
    tags        = body['tags']
    username    = body.get('username')  
    # Add username to the request payload
    
    if not username:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Username not provided'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    unauthorized_urls = []
    deleted_any       = False
    
    for url in urls:
        # retrieve all items from dynamodb 
        response      = dynamodb.scan(
            TableName        = DB_NAME,
            FilterExpression = 'ThumbnailURL = :val',
            ExpressionAttributeValues={':val': {'S': url}}
        )
        
        items = response['Items']
        if not items:
            print(f"No items found for URL: {url}")
            continue
        
        item = items[0]
        
        # Define list of urls that user unauthorized to delete     
        if item['UserName']['S'] != username:
            print(f"User {username} is not authorized to update tags for image uploaded by {item['UserName']['S']}")
            unauthorized_urls.append(url)
            continue
        else:
            deleted_any = True
        current_tags    = json.loads(item['Tags']['S'])
        
        if action_type == 1:    # Add tags
            for tag in tags:
                current_tags.append(tag)
        elif action_type == 0:  # Remove tags
            current_tags = [tag for tag in current_tags if tag not in tags]
        # Updates tag from DynamoDB
        dynamodb.update_item(
            TableName = DB_NAME,
            Key       = {'ImageKey': {'S': item['ImageKey']['S']}},
            UpdateExpression='SET Tags = :val',
            ExpressionAttributeValues={':val': {'S': json.dumps(current_tags)}}
        )
    
    # Prints return messages 
    if deleted_any:
        if len(unauthorized_urls) < len(urls) and len(unauthorized_urls)!= 0:
            message = f'Tags updated successfully, but user {username} is not authorized to update tags for the following URLs: {unauthorized_urls}'
        elif len(unauthorized_urls) == len(urls):
            message = f'User {username} is not authorized to update tags for the following URLs: {unauthorized_urls}'
        else:
            message = 'Tags updated successfully'
    else:
        message     = 'No Tags updated'
    
    response = {
        'statusCode': 200,
        'body': json.dumps({'message': message}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    
    print('Response:', json.dumps(response))
    
    return response
