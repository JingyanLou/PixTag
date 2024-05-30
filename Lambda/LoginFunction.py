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

        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId='1uhreh7q8vorr8rqfo74i8bn39',  # Replace with your Cognito App Client ID
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        # Log the response for debugging
        print(f"Cognito response: {response}")

        if 'AuthenticationResult' not in response:
            if 'ChallengeName' in response:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'Authentication challenge required',
                        'challenge': response['ChallengeName']
                    })
                }
            else:
                raise KeyError("AuthenticationResult not in response")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login successful!',
                'token': response['AuthenticationResult']['IdToken']
            })
        }

    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"KeyError: {str(e)}"})
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"ClientError: {e.response['Error']['Message']}")
        if error_code == "NotAuthorizedException":
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid username or password'})
            }
        elif error_code == "UserNotConfirmedException":
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'User is not confirmed. Please check your email for the confirmation link.'})
            }
        return {
            'statusCode': 400,
            'body': json.dumps({'error': e.response['Error']['Message']})
        }
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
