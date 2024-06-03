import json
import boto3

# We use ChatGPT to help achieve this feature.
# Initialize the SNS client
sns = boto3.client('sns')
# Define the SNS topic ARN
TOPIC_ARN = "arn:aws:sns:us-east-1:261491978824:Tag"  # Replace with SNS Topic ARN

def lambda_handler(event, context):
    """
    Lambda function handler to process incoming requests and fetch subscribed tags for a given username.
    """
    print(f"Received event: {json.dumps(event)}")
    try:
        # Check if 'queryStringParameters' exists in the event
        if 'queryStringParameters' not in event or not event['queryStringParameters']:
            raise ValueError("Missing 'queryStringParameters' in the event")

        # Extract the username from query parameters
        username = event['queryStringParameters'].get('username')
        if not username:
            raise ValueError("Missing 'username' in the query parameters")

        # Fetch the subscribed tags for the given username
        tags = get_subscribed_tags(username)

        # Prepare the response body
        response_body = {'tags': tags}
        print(f"Response body: {json.dumps(response_body)}")

        # Return a successful response
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
        # Handle any exceptions that occur
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
    """
    Fetches the subscribed tags for a given username by listing the subscriptions and checking their filter policies.
    """
    try:
        print(f"Fetching subscriptions for username: {username}")
        # List subscriptions for the given topic
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
        tags = []
        # Iterate through subscriptions to find the matching username
        for sub in subscriptions['Subscriptions']:
            if sub['Endpoint'] == username:
                # Get subscription attributes for each matching subscription
                response = sns.get_subscription_attributes(SubscriptionArn=sub['SubscriptionArn'])
                attributes = response['Attributes']
                # Load the filter policy
                filter_policy = json.loads(attributes.get('FilterPolicy', '{}'))
                # Add the tags to the list if they exist in the filter policy
                if 'tag' in filter_policy:
                    tags.extend(filter_policy['tag'])
        print(f"Found tags: {tags}")
        return tags
    except Exception as e:
        # Handle any exceptions that occur while fetching tags
        print(f"Error getting subscribed tags: {str(e)}")
        return []
