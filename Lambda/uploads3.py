import json
import base64
import boto3
import os

s3_client = boto3.client('s3')
BUCKET_NAME = 'imagesforassignment3'

def lambda_handler(event, context):
    print("Lambda function has started execution.")
    
    try:
        print("Received event:", json.dumps(event))  # Log the received event

        # Ensure the body exists in the event
        if 'body' not in event:
            raise ValueError("Missing 'body' in event")
        else:
            print("'body' found in event.")
            print("Event body type:", type(event['body']))  # Log the type of 'body'

        # Check if the body is a string or dict
        body_str = event['body'] if isinstance(event['body'], str) else json.dumps(event['body'])
        body = json.loads(body_str)
        print("Parsed body:", body)  # Log the parsed body

        # Ensure required fields are present in the body
        if 'file' not in body or 'name' not in body or 'username' not in body:
            raise ValueError("Missing required fields in body")
        else:
            print("All required fields found in body.")

        base64_image = body['file']
        image_name = body['name']
        username = body['username']

        # Decode the Base64 image
        print("Decoding Base64 image.")
        image_data = base64.b64decode(base64_image)
        print("Image decoded successfully.")

        # Create the S3 key
        s3_key = f'images/{username}/{image_name}'
        print(f"S3 key created: {s3_key}")

        # Upload the image to S3
        print("Uploading image to S3.")
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=image_data)
        print("Image uploaded to S3 successfully.")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image uploaded successfully!'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            }
        }

    except Exception as e:
        print("Error occurred:", str(e))  # Log the error
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            }
        }