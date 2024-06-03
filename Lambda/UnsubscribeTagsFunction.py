import json
import boto3
# We use ChatGPT to help achieve this feature.
# Initialize SNS client
sns = boto3.client('sns')
# Define the SNS topic ARN
TOPIC_ARN = "arn:aws:sns:us-east-1:261491978824:Tag"  # Please enter the TOPIC ARN

def get_subscription_arn(email):
    """
    Fetches the subscription ARN for a given email.
    """
    try:
        print(f"Fetching subscription ARN for email: {email}")
        # List subscriptions for the given topic
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
        # Iterate through subscriptions to find the matching email
        for sub in subscriptions['Subscriptions']:
            if sub['Endpoint'] == email:
                print(f"Found subscription ARN: {sub['SubscriptionArn']}")
                return sub['SubscriptionArn']
        return None
    except Exception as e:
        print(f"Error getting subscriptions: {str(e)}")
        return None

def remove_tag_from_filter_policy(subscription_arn, tag, username):
    """
    Removes a specified tag from the filter policy of the given subscription ARN.
    Unsubscribes the user if no tags remain.
    """
    try:
        print(f"Removing tag from filter policy for subscription ARN: {subscription_arn} with tag: {tag}")
        # Get subscription attributes
        response = sns.get_subscription_attributes(SubscriptionArn=subscription_arn)
        print(f"Subscription attributes: {response}")

        attributes = response['Attributes']
        # Load the current filter policy
        filter_policy = json.loads(attributes.get('FilterPolicy', '{}'))
        print(f"Current filter policy: {filter_policy}")

        # Remove the specified tag from the filter policy
        if 'tag' in filter_policy and tag in filter_policy['tag']:
            filter_policy['tag'].remove(tag)

        # Remove empty arrays from filter policy, except for 'username'
        filter_policy = {k: v for k, v in filter_policy.items() if v or k == 'username'}

        if not filter_policy.get('tag'):
            # Unsubscribe if no tags remain
            sns.unsubscribe(SubscriptionArn=subscription_arn)
            print(f"Unsubscribed {subscription_arn} as no tags remain")
            return True, "Unsubscribed successfully as no tags remain"
        else:
            # Update the subscription filter policy
            sns.set_subscription_attributes(
                SubscriptionArn=subscription_arn,
                AttributeName='FilterPolicy',
                AttributeValue=json.dumps(filter_policy)
            )
            print(f"Subscription updated with new filter policy: {json.dumps(filter_policy)}")
            return True, f"Unsubscribed tag {tag} for username {username}"
    except Exception as e:
        print(f"Error updating filter policy: {str(e)}")
        return False, f"Error updating filter policy: {str(e)}"

def lambda_handler(event, context):
    """
    Lambda function handler to process incoming requests.
    """
    print(f"Received event: {json.dumps(event)}")
    try:
        # Parse the body of the event
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            data = event  # In case the event is already a dictionary and not string-encoded

        print(f"Parsed data: {data}")

        # Extract required fields from the parsed data
        email = data.get('username')
        tag = data.get('tag')
        username = data.get('username')

        # Check for missing required fields
        missing_fields = []
        if not email:
            missing_fields.append('email')
        if not tag:
            missing_fields.append('tag')
        if not username:
            missing_fields.append('username')

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Get the subscription ARN for the provided email
        subscription_arn = get_subscription_arn(email)
        if subscription_arn:
            # Remove the tag from the filter policy
            success, message = remove_tag_from_filter_policy(subscription_arn, tag, username)
        else:
            success, message = False, "Subscription not found for email."

        # Set the appropriate status code based on the operation result
        status_code = 200 if success else 500
        print(f"Operation result: {message}")

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        message = f"Error processing request: {str(e)}"
        status_code = 500

    # Return the response with status code and message
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        }
    }
