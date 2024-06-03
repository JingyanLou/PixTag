import json
import boto3
from botocore.exceptions import ClientError

# We use ChatGPT to help achieve this feature.
# Initialize the Cognito client
cognito_client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    try:
        # Check if 'body' is present in the event
        if 'body' not in event:
            raise KeyError("Missing 'body' in event")

        # Parse the body of the event
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']

        # Extract the username and password from the body
        username = body['username']
        password = body['password']

        # Initiate the authentication request to Cognito
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

        # Check if the response contains the 'AuthenticationResult'
        if 'AuthenticationResult' not in response:
            # Handle authentication challenges if present
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

        # Return a successful login response with the token
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login successful!',
                'token': response['AuthenticationResult']['IdToken']
            })
        }

    except KeyError as e:
        # Handle KeyError exceptions
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"KeyError: {str(e)}"})
        }
    except ClientError as e:
        # Handle ClientError exceptions from Cognito
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
        # Handle other ClientError exceptions
        return {
            'statusCode': 400,
            'body': json.dumps({'error': e.response['Error']['Message']})
        }
    except Exception as e:
        # Handle any other exceptions
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
