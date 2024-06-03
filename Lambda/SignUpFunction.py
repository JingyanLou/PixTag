import json
import boto3
from botocore.exceptions import ClientError

# We use ChatGPT to help achieve this feature.
# Initialize the Cognito client
cognito_client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    try:
        # Check if 'body' is in the event
        if 'body' not in event:
            raise KeyError("Missing 'body' in event")
        
        # Parse the body of the event
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']

        # Extract user details from the body
        username = body['username']
        password = body['password']
        email = body['email']
        firstname = body['firstname']
        lastname = body['lastname']

        # Sign up the user with Cognito
        response = cognito_client.sign_up(
            ClientId='1uhreh7q8vorr8rqfo74i8bn39',  # Replace with your actual ClientId
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'given_name', 'Value': firstname},
                {'Name': 'family_name', 'Value': lastname}
            ]
        )

        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Sign up successful! Please verify your email.'})
        }
    except ClientError as e:
        # Handle known ClientError exceptions from Cognito
        error_message = e.response['Error']['Message']
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_message})
        }
    except Exception as e:
        # Handle any other exceptions
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
