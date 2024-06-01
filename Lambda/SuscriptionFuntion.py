import json
import boto3

sns = boto3.client('sns')
TOPIC_ARN = ""  # Please enter the TOPIC ARN

def get_subscription_arn(email):
    try:
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
        for sub in subscriptions['Subscriptions']:
            if sub['Endpoint'] == email:
                return sub['SubscriptionArn']
        return None
    except Exception as e:
        print(f"Error getting subscriptions: {str(e)}")
        return None

def update_filter_policy(subscription_arn, tag):
    try:
        response = sns.get_subscription_attributes(SubscriptionArn=subscription_arn)
        attributes = response['Attributes']
        filter_policy = json.loads(attributes.get('FilterPolicy', '{}'))

        if 'tag' not in filter_policy:
            filter_policy['tag'] = []
        if tag not in filter_policy['tag']:
            filter_policy['tag'].append(tag)
            sns.set_subscription_attributes(
                SubscriptionArn=subscription_arn,
                AttributeName='FilterPolicy',
                AttributeValue=json.dumps(filter_policy)
            )
            return True, f"Subscription updated with tag {tag}"
        else:
            return False, f"Tag {tag} is already subscribed"
    except Exception as e:
        print(f"Error updating filter policy: {str(e)}")
        return False, "Error updating filter policy"

def create_subscription(email, tag, username):
    try:
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
        return True, f"Subscription created for {email} with tag {tag}"
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        return False, "Error creating subscription"

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        email = data['email']
        tag = data['tag']
        username = data['username']

        subscription_arn = get_subscription_arn(email)
        if subscription_arn:
            success, message = update_filter_policy(subscription_arn, tag)
        else:
            success, message = create_subscription(email, tag, username)

        status_code = 200 if success else 500

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        message = "Error processing request"
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
