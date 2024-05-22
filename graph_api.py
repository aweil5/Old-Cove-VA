import msal
from msal import PublicClientApplication
from assistant import help_user, create_thread
import webbrowser
import requests
import json
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# READ IN GLOBAL VARIABLES FROM ENV FILE
APPLICATION_ID = os.environ.get('APPLICATION_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
asistant_id = os.environ.get('OPENAI_ASSISTANT_ID')

authority_url = "https://login.microsoftonline.com/organizations/"

BASE_URL = "https://graph.microsoft.com/v1.0/"

ENDPOINT = BASE_URL + "me/messages"

SCOPES = ['User.Read', 'Mail.ReadBasic', 'Mail.Read', 'Mail.ReadWrite', 'Mail.Send']

# Define a constant for the cache file path
TOKEN_CACHE_FILE = "token_cache.bin"

def login_access_token():
    # Create or load a token cache to prevent constant reauthentication
    token_cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "rb") as f:
            token_cache.deserialize(f.read())
    # Creates app object for the microsoft application on Azure
    app = PublicClientApplication(
        APPLICATION_ID,
        authority = authority_url,
        token_cache=token_cache
    )

    # Checks if the token_cache has any authorized accounts already
    accounts = app.get_accounts()

    if accounts:
        # If an account exists in the cache, attempt to acquire token silently
        result = app.acquire_token_silent(scopes=SCOPES, account=accounts[0])
        if result:
            # Token acquired successfully from cache
            return result['access_token']
        else:
            # Attempt to acquire token interactively if silent acquisition fails
            result = app.acquire_token_interactive(scopes=SCOPES, account=accounts[0])
            # Serialize token cache to save the newly acquired token
            with open(TOKEN_CACHE_FILE, "wb") as f:
                f.write(token_cache.serialize().encode('utf-8'))  # Convert string to bytes
            return result['access_token']

    else:
        # If no account exists in the cache, initiate device flow for authentication
        flow = app.initiate_device_flow(scopes=SCOPES)
        print(flow)
        print(flow['message'])
        webbrowser.open(flow['verification_uri'])

        # Poll for completion of device flow and acquire token
        result = app.acquire_token_by_device_flow(flow)
        # Serialize token cache to save the newly acquired token
        with open(TOKEN_CACHE_FILE, "wb") as f:
            f.write(token_cache.serialize().encode('utf-8'))  # Convert string to bytes
        return result['access_token']


# Extracts the emails in the whitelisted "Client" Folder
def get_emails(access_token : str):
    headers = {
        'Authorization' : 'Bearer ' + access_token
    }

    # Can Hardcode Folder ID since we know exactly what user will be running this script each time
    FOLDER_ID = "/me/mailFolders/AAMkAGU4NmJiM2E4LTdiMGMtNGE1My1hYjY1LWRlMGE4Y2E1MGJjMAAuAAAAAAD_Fd4hHakzSb8Dz7puAPhoAQDOBYS3gFwMTZ4rTkBHS0CiAAAH3vTOAAA=/messages"
    FOLDER_ENDPOINT = BASE_URL + FOLDER_ID

    # END POINT TO RECIEVE ALL EMAISL IN WHITELIST FOLDER
    response = requests.get(FOLDER_ENDPOINT, headers=headers)
    logging.info(f"Email Reading Status: {response}")
    if response.status_code != 200:
        logging.error("There has been an error when processing your emails")
        return None
    else:
    # Add error handling here to deal with improper Request Call
        return response.json()

# ----- Changes Email Status to Read to ensure it does not get responded to again -----#
def update_email(email_id : str, access_token:str):
    ENDPOINT = BASE_URL + f"me/messages/{email_id}"
    request_body = {
    "isRead": True
    }
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    # Send the PATCH request with JSON body
    result = requests.patch(ENDPOINT, json=request_body, headers=headers)
    return result

def flag_email(email_id : str, access_token:str):
    ENDPOINT = BASE_URL + f"me/messages/{email_id}"
    request_body = {
    "flag": {
        'flagStatus': 'flagged'
    }
    }
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    # Send the PATCH request with JSON body
    result = requests.patch(ENDPOINT, json=request_body, headers=headers)
    return result

def send_message(assistant_response : str , email_id : str, access_token:str , name : str):
    response = assistant_response
    # Personalize Message
    if name != "NO_NAME":
        space_index = name.find(' ')  # Find the index of the first space
        if space_index != -1:  # If a space is found
            response = f"Hello {name[:space_index]}, \n\n" + assistant_response
        else:
            response = f"Hello {name}, \n\n" + assistant_response

        
    # Finish response with conference meeting
    response = response + "\n\n If these tips did not help you, then here is a link to schedule a time to meet with Andrew. \n\n Schedule a call with Andrew: https://calendly.com/oldcove/15min"

    ENDPOINT = BASE_URL + f"/me/messages/{email_id}/reply"

    email_body = {
        "message" : {
            "body": {
                "content":response
            }
        }
    }
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    result = requests.post(ENDPOINT, json=email_body, headers=headers)
    return result


# Main Function that processes and sends out email responses
def read_and_send_emails():
    access_token = login_access_token()
    emails = get_emails(access_token)
    if emails:
        for message in emails['value']:
            if message['isRead'] is False:
                # Calls the Assistant and gets their response
                ai_response = help_user(str(message['body']), create_thread())
                # If help_user fails ie chatgpt encountered an error, then do not respond and flag the email to be viewed by
                # a person
                if ai_response != "ERROR":
                    # Logic to determine if we can find the sender's name, makes email more personable
                    if message['sender']['emailAddress']['name']:
                        send_message(ai_response, message['id'], access_token, message['sender']['emailAddress']['name'])
                    else:
                        send_message(ai_response, message['id'], access_token, "NO_NAME")
                else:
                    logging.error("Encounterd an Error When Responding to an Email")
                    flag_email(message['id'], access_token)
                update_email(message['id'], access_token)

    logging.info("Finished replying to Emails: 200")


def get_folder_id(access_token : str):
    ENDPOINT = "https://graph.microsoft.com/v1.0/me/mailFolders"
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.get(ENDPOINT, headers=headers)
    print(response.json())


