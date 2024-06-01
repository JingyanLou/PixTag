import json
import boto3

dynamodb = boto3.client('dynamodb')
DB_NAME  = 'ImageLabels'

def lambda_handler(event, context):
    body = json.loads(event['body'])
    thumbnail_url = body['thumbnail_url']
    
    response = dynamodb.scan(
        TableName= DB_NAME,
        FilterExpression='ThumbnailURL = :val',
        ExpressionAttributeValues={':val': {'S': thumbnail_url}}
    )
    
    items = response['Items']
    if items:
        fullsize_url = items[0]['S3ImageURL']['S']
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
