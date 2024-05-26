
import openai
from dotenv import load_dotenv
import time
import logging
from datetime import datetime
import os
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import json

load_dotenv()
client = openai.OpenAI()


# Init Logger
logger = logging.getLogger(__name__)

# === Hardcode our ids ==
assistant_id1 = os.environ.get("OPENAI_ASSISTANT_ID")

def create_thread():
    thread = client.beta.threads.create(
    )
    return thread.id

# ==== Create a Message ====
def help_user(client_message:str, thread_id : str):
    message = client_message

    # Use thread we generated to attatch to our assistant
    message = client.beta.threads.messages.create(
    thread_id=thread_id, role="user", content=message
    )

    # === Run our Assistant ===

    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=str(assistant_id1),
    instructions="Please make the instructions very clear and as concise as possible. DO NOT WRITE ANY FROM OF INTRODUCTION. Seperate each tip with 2 newlines and number each tip. Answer their message and only their message. End the message with a kind goodbye and signing the email with your name, Doug.",
    )


    # === Run ===
    message = wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

    if message:
        return message
    else:
        return "ERROR"


def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
# """
# Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
# :param thread_id: The ID of the thread.
# :param run_id: The ID of the run.
# :param sleep_interval: Time in seconds to wait between checks.
# """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
                
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)



# Function definitions for model to call 
# Each will have its own unique assistant to call depending on needs of email type
def handle_simple_tech_help(message : str):
    print("Handling Tech Help Email.")

def handle_billing():
    print("Handling Billing email.")

def handle_walkthrough(message : str, location : str  = "NO ADDRESS PROVIDED"):
    print(f"Handling Walkthrough Email at {location}")

def handle_other():
    print("Could not determine email type")

def email_analysis():
    
    # Test Message
    messages = [{"role": "user", 
                 "content": "I would like to schedule a walkthrough for an upcoming project in cos cob connecticut",}]

    # WRITING ALL THE FUNCTIONS IN A JSON LIST THAT THE MODEL IS CAPABLE OF CALLING
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handle_walkthrough",
                "description": "This will handle scheduling a walkthrough for a client",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type" : "string",
                            "description": "This will be the actual content that is being analyzed, but with all the html tags removed.",
                        },
                        "location": {
                            "type": "string",
                            "description": """The location where the walkthrough would take place. This can be in the
                            form of an address or a city. Eg 113 lower crest rd, or Cos Cob Connecticut. """,
                        },
                    },
                },
                "required": ["message"],
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_simple_tech_help",
                "description": "This function will assist a user ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "This will be the actual content that is being analyzed, but with all the html tags removed.",
                        },
                        
                    },
                    "required": ["message"]
                },
            }
        },
    ]

    return




