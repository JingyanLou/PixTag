import json
import boto3
import urllib.parse
from botocore.exceptions import BotoCoreError, ClientError

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
S3BUCKET = 'pixtag-yzhu-bucket'
DB_NAME = 'ImageLabels'

def lambda_handler(event, context):
    try:
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                body = json.loads(body)
            else:
                body = body
        else:
            body = event                 # In case the event is already a dictionary and not string-encoded
        
        urls = body.get('url', [])
        username = body.get('username')  # Add username to the request payload
        
        if not urls:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'No URLs provided'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        
        unauthorized_urls = []
        deleted_any = False
        for url in urls:
            try:
                # Find the item in DynamoDB
                response = dynamodb.scan(
                    TableName=DB_NAME,
                    FilterExpression         = 'ThumbnailURL = :val',
                    ExpressionAttributeValues= {':val': {'S': url}}
                )
                
                # Reports if image not found 
                items = response.get('Items', [])
                if not items:
                    print(f"No item found in DynamoDB for URL: {url}")
                    continue
                
                item          = items[0]
                item_username = item['UserName']['S']
                
                # To extract list of image urls that user not authorized to delete  
                if item_username != username:
                    print(f"User {username} is not authorized to delete image uploaded by {item_username}")
                    unauthorized_urls.append(url)
                    continue

                image_key     = item['ImageKey']['S']
                s3_image_path = item['S3ImagePath']['S']
                thumbnail_url = item['ThumbnailURL']['S']
                print('s3_image_path : ', s3_image_path)
                
                # Extract the thumbnail keys
                s3_thumbnail_key = urllib.parse.unquote('thumbnails/' + '/'.join(thumbnail_url.split('/')[-2:]))
                print('s3_thumbnail_key : ', s3_thumbnail_key)
                
                # Delete image and thumbnail from S3
                try:
                    s3.delete_object(Bucket=S3BUCKET, Key=s3_image_path)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchKey':
                        print(f"No image found in S3 for key: {s3_image_path}")
                    else:
                        raise

                try:
                    s3.delete_object(Bucket=S3BUCKET, Key=s3_thumbnail_key)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchKey':
                        print(f"No thumbnail found in S3 for key: {s3_thumbnail_key}")
                    else:
                        raise
                
                # Delete item from DynamoDB
                try:
                    dynamodb.delete_item(
                        TableName=DB_NAME,
                        Key={'ImageKey': {'S': image_key}}
                    )
                    deleted_any = True
                except ClientError as e:
                    print(f"Error deleting item from DynamoDB for key: {image_key}, error: {e}")
            
            except (BotoCoreError, ClientError) as e:
                print(f"Error processing URL {url}: {e}")
                continue
        
        # Return messages 
        if deleted_any:
            if len(unauthorized_urls) < len(urls) and len(unauthorized_urls) != 0:
                message = f'Images deleted successfully, but user {username} is not authorized to delete the following URLs: {unauthorized_urls}'
            elif len(unauthorized_urls) == len(urls):
                message = f'User {username} is not authorized to delete the following URLs: {unauthorized_urls}'
            else:
                message = 'Images deleted successfully'
        else:
            message = 'No images deleted'
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': message}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON format'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    
    except Exception as e:
        print(f"Unhandled exception: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
