import json
import boto3
from   boto3.dynamodb.conditions import Attr


def lambda_handler(event, context):
    try:
        # Parsing incoming JSON request
        body = json.loads(event['body'])
        tags = body['tags']
        
        # Generates a tag dictionary 
        tag_dict = {}
        for tag in tags:
            try:
                name, count = tag.split(',')
                tag_dict[name.strip()] = int(count.strip())
            except ValueError as e:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Invalid tag format: {tag}. Expected format "tag1:count, tag2:count".'}),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'}
                        }
        
        # Initialize DynamoDB client
        dynamodb =  boto3.resource('dynamodb')
        table    = dynamodb.Table('ImageTags')
        
        # Scan the table and filter items manually
        response = table.scan()
        items    = response['Items']
        
        # Filter the items based on the tag counts
        filtered_items = []
        for item in items:
            tag_counts = {tag: item['tags'].count(tag) for tag in tag_dict.keys()}
            if all(tag_counts[tag] >= tag_dict[tag]    for tag in tag_dict.keys()):
                filtered_items.append(item['imageUrl'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({'links': filtered_items}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS, POST',
                'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS, POST',
            'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
            } 
        }