import json
import boto3

sns = boto3.client('sns')
TOPIC_ARN = "arn:aws:sns:us-east-1:261491978824:Tag"  # Please enter the TOPIC ARN

def get_subscription_arn(email):
    try:
        print(f"Fetching subscription ARN for email: {email}")
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
        for sub in subscriptions['Subscriptions']:
            if sub['Endpoint'] == email:
                print(f"Found subscription ARN: {sub['SubscriptionArn']}")
                return sub['SubscriptionArn']
        return None
    except Exception as e:
        print(f"Error getting subscriptions: {str(e)}")
        return None

def update_filter_policy(subscription_arn, tag, username):
    try:
        print(f"Updating filter policy for subscription ARN: {subscription_arn} with tag: {tag}")
        response = sns.get_subscription_attributes(SubscriptionArn=subscription_arn)
        attributes = response['Attributes']
        filter_policy = json.loads(attributes.get('FilterPolicy', '{}'))

        if 'tag' not in filter_policy:
            filter_policy['tag'] = []
        if tag not in filter_policy['tag']:
            filter_policy['tag'].append(tag)

        if 'username' not in filter_policy:
            filter_policy['username'] = []
        if username not in filter_policy['username']:
            filter_policy['username'].append(username)

        sns.set_subscription_attributes(
            SubscriptionArn=subscription_arn,
            AttributeName='FilterPolicy',
            AttributeValue=json.dumps(filter_policy)
        )
        print(f"Subscription updated with new filter policy: {json.dumps(filter_policy)}")
        return True, f"Subscription updated with tag {tag} and username {username}"
    except Exception as e:
        print(f"Error updating filter policy: {str(e)}")
        return False, "Error updating filter policy"

def create_subscription(email, tag, username):
    try:
        print(f"Creating new subscription for email: {email} with tag: {tag} and username: {username}")
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
        print(f"Error creating subscription: {str(e)}")
        return False, "Error creating subscription"

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    try:
        if 'body' in event:
            body = event['body']
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            data = event  # In case the event is already a dictionary and not string-encoded

        print(f"Parsed data: {data}")

        email = data.get('username')
        tag = data.get('tag')
        username = data.get('username')

        missing_fields = []
        if not email:
            missing_fields.append('email')
        if not tag:
            missing_fields.append('tag')
        if not username:
            missing_fields.append('username')

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        subscription_arn = get_subscription_arn(email)
        if subscription_arn:
            success, message = update_filter_policy(subscription_arn, tag, username)
        else:
            success, message = create_subscription(email, tag, username)

        status_code = 200 if success else 500
        print(f"Operation result: {message}")

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        message = f"Error processing request: {str(e)}"
        status_code = 500

    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        }
    }
