import json
import boto3

s3 = boto3.client('s3')

dynamodb = boto3.client('dynamodb')
S3BUCKET = 'jy.bucket'
DB_NAME = 'ImageLabels'

def lambda_handler(event, context):
    body = json.loads(event['body'])
    urls = body['url']
    
    for url in urls:
        # Find the item in DynamoDB
        response = dynamodb.scan(
            TableName= DB_NAME,
            FilterExpression='ThumbnailURL = :val',
            ExpressionAttributeValues={':val': {'S': url}}
        )
        
        items = response['Items']
        if not items:
            continue
        
        item = items[0]
        image_key = item['ImageKey']['S']
        s3_image_path = item['S3ImagePath']['S']
        thumbnail_url = item['ThumbnailURL']['S']
        
        # Extract the S3 keys from the URLs
        s3_thumbnail_key = '/'.join(thumbnail_url.split('/')[-4:])
        
        # Delete image and thumbnail from S3
        s3.delete_object(Bucket=S3BUCKET, Key=s3_image_path)
        s3.delete_object(Bucket=S3BUCKET, Key=s3_thumbnail_key)
        
        # Delete item from DynamoDB
        dynamodb.delete_item(
            TableName = DB_NAME,
            Key={'ImageKey': {'S': image_key}}
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Images deleted successfully'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
