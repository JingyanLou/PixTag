import json
import boto3

sns = boto3.client('sns')
TOPIC_ARN = "arn:aws:sns:us-east-1:261491978824:Tag"  # Replace with SNS Topic ARN

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    try:
        # Check if 'queryStringParameters' exists in the event
        if 'queryStringParameters' not in event or not event['queryStringParameters']:
            raise ValueError("Missing 'queryStringParameters' in the event")

        username = event['queryStringParameters'].get('username')
        if not username:
            raise ValueError("Missing 'username' in the query parameters")

        # Fetch the subscribed tags for the given username
        tags = get_subscribed_tags(username)

        response_body = {'tags': tags}
        print(f"Response body: {json.dumps(response_body)}")

        return {
            'statusCode': 200,
            'body': json.dumps(response_body),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            }
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f"Error processing request: {str(e)}"}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
            }
        }

def get_subscribed_tags(username):
    try:
        print(f"Fetching subscriptions for username: {username}")
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
        tags = []
        for sub in subscriptions['Subscriptions']:
            if sub['Endpoint'] == username:
                response = sns.get_subscription_attributes(SubscriptionArn=sub['SubscriptionArn'])
                attributes = response['Attributes']
                filter_policy = json.loads(attributes.get('FilterPolicy', '{}'))
                if 'tag' in filter_policy:
                    tags.extend(filter_policy['tag'])
        print(f"Found tags: {tags}")
        return tags
    except Exception as e:
        print(f"Error getting subscribed tags: {str(e)}")
        return []
