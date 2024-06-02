import json
import boto3
from image_detection_import import obj_detect

DB_NAME = 'ImageLabels'
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))  # Log the received event

        # Ensure the body exists in the event
        if 'body' not in event:
            raise ValueError("Missing 'body' from event")
        else:
            print("Event body type:", type(event['body']))  # Log the type of 'body'

        # Check if the body is a string or dict
        body_str = event['body'] if isinstance(event['body'], str) else json.dumps(event['body'])
        body = json.loads(body_str)
        print("Parsed body:", body)  # Log the parsed body

        # Ensure required fields are present in the body
        if 'file' not in body or 'username' not in body:
            raise ValueError("Missing required fields in body")

        base64_image = body['file']
        username = body['username']
        print('Base64 image:', base64_image)
        print('Username:', username)

        # Detect objects in the image
        detected_object = json.loads(obj_detect(base64_image))
        detected_labels = set(obj['label'] for obj in detected_object)
        print('Detected labels:', detected_labels)

        # Scan DynamoDB for images with matching tags
        matching_images = []
        response = dynamodb.scan(
            TableName=DB_NAME,
            FilterExpression='UserName = :username',
            ExpressionAttributeValues={':username': {'S': username}}
        )
        print("DynamoDB scan response:", json.dumps(response))  # Log the DynamoDB response

        # Scan through all images such containing all of the tags from sent images
        for item in response['Items']:
            tags = set(json.loads(item['Tags']['S']))  # Load the tags and convert to a set
            if detected_labels.issubset(tags):  # Check if all detected labels are in the tags
                matching_images.append(item['ThumbnailURL']['S'])  # Append the thumbnail URL if all labels match

        print("Matching images:", matching_images)  # Log the matching images

        if matching_images:
            return {
                'statusCode': 200,
                'body': json.dumps({'links': matching_images}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No matching images found'}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

    except Exception as e:
        print("Exception:", str(e))  # Log the exception
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
