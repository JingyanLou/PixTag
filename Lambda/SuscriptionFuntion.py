import json
import boto3

# We use ChatGPT to help achieve this feature.
# Initialize the SNS client
sns = boto3.client('sns')
# Define the SNS topic ARN
TOPIC_ARN = "arn:aws:sns:us-east-1:261491978824:Tag"  # Please enter the TOPIC ARN

def get_subscription_arn(email):
    """
    Fetches the subscription ARN for a given email.

    Args:
    email (str): The email address to search for.

    Returns:
    str: The subscription ARN if found, None otherwise.
    """
    try:
        print(f"Fetching subscription ARN for email: {email}")
        # List subscriptions for the given SNS topic
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
        
        # Iterate through the subscriptions to find the one matching the email
        for sub in subscriptions['Subscriptions']:
            if sub['Endpoint'] == email:
                print(f"Found subscription ARN: {sub['SubscriptionArn']}")
                return sub['SubscriptionArn']
        # Return None if no matching subscription is found
        return None
    except Exception as e:
        # Log and return None in case of any exceptions
        print(f"Error getting subscriptions: {str(e)}")
        return None

def update_filter_policy(subscription_arn, tag, username):
    """
    Updates the filter policy for a given subscription ARN by adding the specified tag and username.

    Args:
    subscription_arn (str): The subscription ARN.
    tag (str): The tag to add to the filter policy.
    username (str): The username to add to the filter policy.

    Returns:
    tuple: A boolean indicating success and a message string.
    """
    try:
        print(f"Updating filter policy for subscription ARN: {subscription_arn} with tag: {tag}")
        # Get current attributes of the subscription
        response = sns.get_subscription_attributes(SubscriptionArn=subscription_arn)
        attributes = response['Attributes']
        # Load the current filter policy as a dictionary
        filter_policy = json.loads(attributes.get('FilterPolicy', '{}'))

        # Ensure the 'tag' list exists in the filter policy and add the tag if it's not already there
        if 'tag' not in filter_policy:
            filter_policy['tag'] = []
        if tag not in filter_policy['tag']:
            filter_policy['tag'].append(tag)

        # Ensure the 'username' list exists in the filter policy and add the username if it's not already there
        if 'username' not in filter_policy:
            filter_policy['username'] = []
        if username not in filter_policy['username']:
            filter_policy['username'].append(username)

        # Update the subscription filter policy
        sns.set_subscription_attributes(
            SubscriptionArn=subscription_arn,
            AttributeName='FilterPolicy',
            AttributeValue=json.dumps(filter_policy)
        )
        print(f"Subscription updated with new filter policy: {json.dumps(filter_policy)}")
        return True, f"Subscription updated with tag {tag} and username {username}"
    except Exception as e:
        # Log and return error message in case of any exceptions
        print(f"Error updating filter policy: {str(e)}")
        return False, "Error updating filter policy"

def create_subscription(email, tag, username):
    """
    Creates a new subscription with the specified email, tag, and username.

    Args:
    email (str): The email address to subscribe.
    tag (str): The tag to include in the filter policy.
    username (str): The username to include in the filter policy.

    Returns:
    tuple: A boolean indicating success and a message string.
    """
    try:
        print(f"Creating new subscription for email: {email} with tag: {tag} and username: {username}")
        # Create a new subscription with the specified filter policy
        sns.subscribe(
            TopicArn=TOPIC_ARN,
            Protocol='email',
            Endpoint=email,
            Attributes={
                'FilterPolicy': json.dumps({
                    'tag': [tag],
                    'username': [username]
                })
            }
        )
        print(f"Subscription created for {email} with tag {tag}")
        return True, f"Subscription created for {email} with tag {tag}"
    except Exception as e:
        # Log and return error message in case of any exceptions
        print(f"Error creating subscription: {str(e)}")
        return False, "Error creating subscription"

def lambda_handler(event, context):
    """
    Lambda function handler to process incoming requests.
    This function extracts necessary data from the event, validates it,
    and either updates the filter policy of an existing subscription
    or creates a new subscription.

    Args:
    event (dict): The event data passed to the Lambda function.
    context (object): The runtime information of the Lambda function.

    Returns:
    dict: The HTTP response containing status code and message.
    """
    print(f"Received event: {json.dumps(event)}")
    try:
        # Extract the body of the event if it exists
        if 'body' in event:
            body = event['body']
            # Parse the body as JSON if it's a string
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            # Use the event directly if it's already a dictionary
            data = event

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

        # Raise an error if any required fields are missing
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Get the subscription ARN for the provided email
        subscription_arn = get_subscription_arn(email)
        if subscription_arn:
            # Update the filter policy if the subscription exists
            success, message = update_filter_policy(subscription_arn, tag, username)
        else:
            # Create a new subscription if it doesn't exist
            success, message = create_subscription(email, tag, username)

        # Set the appropriate status code based on the operation result
        status_code = 200 if success else 500
        print(f"Operation result: {message}")

    except Exception as e:
        # Log and set the error message and status code in case of any exceptions
        print(f"Error processing request: {str(e)}")
        message = f"Error processing request: {str(e)}"
        status_code = 500

    # Return the HTTP response with status code, message, and headers
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        }
    }
