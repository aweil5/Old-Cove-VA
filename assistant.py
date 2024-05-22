
import openai
from dotenv import load_dotenv
import time
import logging
from datetime import datetime
import os
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

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


def handle_tech():
    print("Handling spam email.")

def handle_billing():
    print("Handling promotional email.")

def handle_walkthrough():
    print("Handling other types of email.")

def handle_other():
    print("Other type")

def email_analysis(client_message : str, thread_id : str):
    # Analyzes Email Body and determines the type of email written
    # Then calls the correct function to get a proper response to the person which will be returned

    email_types = ['TECH_HELP', 'BILLING', 'WALKTHROUGH']

    # Craft the prompt template
    prompt_template = PromptTemplate(
        input_variables=["email_text"],
        template="""
        Analyze the following email and return the type of email. The type of email should be one of the following values:
        - SPAM
        - PROMOTION
        - OTHER
        
        Email:
        {email_text}
        
        Type of email:
        """
    )

    # Initialize the LLMChain
    llm = OpenAI(temperature=0, max_tokens=10)  # Using deterministic settings
    chain = LLMChain(llm=llm, prompt=prompt_template)

    response = chain.run({"email_text": client_message})
    email_type = response.strip().upper()
    
    if email_type == 'TECH_HELP':
        handle_tech()
    elif email_type == 'PROMOTION':
        handle_billing()
    elif email_type == 'WALKTHROUGH':
        handle_walkthrough()
    else:
        handle_other()




