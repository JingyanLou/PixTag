import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME  = 'ImageLabels'

def lambda_handler(event, context):
    # Receiving the thumbnail URL and username
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']
    thumbnail_url = body.get('thumbnail_url')
    username = body.get('username')  # Retrieve the username from the request payload
    
    # Ask for thumbnail URL and username if not present 
    if not thumbnail_url or not username:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Please enter Thumbnail URL and Username'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    try:
        # Extracting values from DynamoDB
        response = dynamodb.scan(
            TableName=DB_NAME,
            FilterExpression='ThumbnailURL = :val AND UserName = :username',
            ExpressionAttributeValues={
                ':val': {'S': thumbnail_url},
                ':username': {'S': username}
            }
        )
        
        items = response.get('Items', [])
        
        # Retrieving corresponding full S3 image URL
        if items:
            fullsize_url = items[0]['S3ImageURL']['S']
            print("Full size URL: ", fullsize_url)
            return {
                'statusCode': 200,
                'body': json.dumps({'fullsize_url': fullsize_url}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        # Else returns a 404 message if URL not found 
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Thumbnail URL not found or not authorized'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
            
    except Exception as e:
        print("Error:", e)  # Log the exception for debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
