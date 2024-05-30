import json
import boto3
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    try:
        if 'body' not in event:
            raise KeyError("Missing 'body' in event")
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']

        username = body['username']
        password = body['password']
        email = body['email']
        firstname = body['firstname']
        lastname = body['lastname']

        response = cognito_client.sign_up(
            ClientId='1uhreh7q8vorr8rqfo74i8bn39',
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'given_name', 'Value': firstname},
                {'Name': 'family_name', 'Value': lastname}
            ]
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Sign up successful! Please verify your email.'})
        }
    except ClientError as e:
        error_message = e.response['Error']['Message']
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_message})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
