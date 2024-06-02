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

def remove_tag_from_filter_policy(subscription_arn, tag, username):
    try:
        print(f"Removing tag from filter policy for subscription ARN: {subscription_arn} with tag: {tag}")
        response = sns.get_subscription_attributes(SubscriptionArn=subscription_arn)
        print(f"Subscription attributes: {response}")

        attributes = response['Attributes']
        filter_policy = json.loads(attributes.get('FilterPolicy', '{}'))
        print(f"Current filter policy: {filter_policy}")

        if 'tag' in filter_policy and tag in filter_policy['tag']:
            filter_policy['tag'].remove(tag)

        # Remove empty arrays from filter policy, except for 'username'
        filter_policy = {k: v for k, v in filter_policy.items() if v or k == 'username'}

        if not filter_policy.get('tag'):
            sns.unsubscribe(SubscriptionArn=subscription_arn)
            print(f"Unsubscribed {subscription_arn} as no tags remain")
            return True, "Unsubscribed successfully as no tags remain"
        else:
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
            success, message = remove_tag_from_filter_policy(subscription_arn, tag, username)
        else:
            success, message = False, "Subscription not found for email."

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
