import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME = 'ImageLabels'

def lambda_handler(event, context):
    print("Received event:", event)  # Log the event for debugging
    
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']
    
    thumbnail_url = body.get('thumbnail_url')
    if not thumbnail_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Thumbnail URL is required'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    try:
        response = dynamodb.scan(
            TableName=DB_NAME,
            FilterExpression='ThumbnailURL = :val',
            ExpressionAttributeValues={':val': {'S': thumbnail_url}}
        )
        
        items = response.get('Items', [])
        print("DynamoDB scan response:", items)  # Log the DynamoDB response for debugging
        
        if items:
            fullsize_url = items[0]['S3ImageURL']['S']
            print("Full size URL: ",fullsize_url)
            return {
                'statusCode': 200,
                'body': json.dumps({'fullsize_url': fullsize_url}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Thumbnail URL not found'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
    except Exception as e:
        print("Error querying DynamoDB:", e)  # Log the exception for debugging
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
