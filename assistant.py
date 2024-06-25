import openai
from dotenv import load_dotenv
import time
import logging
from datetime import datetime
import os
import json

load_dotenv()
client = openai.OpenAI()


# Init Logger
logger = logging.getLogger(__name__)

# === Hardcode our ids ==
assistant_id1 = os.environ.get("OPENAI_ASSISTANT_ID")


def create_thread():
    thread = client.beta.threads.create()
    return thread.id


# ==== Create a Message ====
def help_user(client_message: str, thread_id: str):
    message = client_message

    # Use thread we generated to attatch to our assistant
    message = client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=message
    )

    # === Run our Assistant ===

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=str(assistant_id1),
        instructions="Please make the instructions very clear and as concise as possible. Answer the users tech help if you are confident in your answer. Otherwise recognize you did not understand their message and call the function provided. DO NOT WRITE ANY FROM OF INTRODUCTION. End the message with a kind goodbye and signing the email with your name, Doug.",
    )

    # === Run ===
    message = wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

    if message:
        return message
    else:
        return "ERROR"


def handle_appointment(appointment_type: str):
    if appointment_type == 'CONFERENCE-TECH-HELP':
        print("need conference")
        return "it looks like you need a conference call, here is the link to schedule time : https://schedumle.com"
    if appointment_type == "ESTIMATE":
        print("need estimate")
        return "it looks like you need to schedule an estimate, here is the link to schedule time : https://schedumle.com"
    if appointment_type == "WALKTHROUGH":
        print("need WALKTHROUGH")
        return "it looks like you need to schedule an estimate, here is the link to schedule time : https://schedumle.com"
    else:
        print("I could not fully understand your needs from your message, here is time to schedule for us to talk. https://schedumle.com")


# Analysis of Run State
# This is where we check if any other function calls are required
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
            status = run.status
            # print(f"Current Status: {status}")
            if run.status == "requires_action":

                # Parsing required action
                required_action = run.required_action.submit_tool_outputs.model_dump()
                
                tools_output = []
                # Analyze all necessary functions to call
                for action in required_action["tool_calls"]:
                    function_name = action['function']['name']
                    arguments = json.loads(action['function']['arguments'])
                    print(action)

                    # Cases for different available functions
                    if function_name == "handle_appointment":
                        output = handle_appointment(arguments['appointment_type'])
                        tools_output.append(
                            {
                                'tool_call_id': action['id'],
                                'output' : output
                            }
                        )
                    else:
                        print("FUNCTION NOT FOUND")
                # Submit Tool output back to Assistant

                print("fin the function calls")
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id = thread_id,
                    run_id = run_id,
                    tool_outputs = tools_output
                )



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
                print(response)
                
                return response

        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


help_user("I need to confernce with you about my sonos amp. Nothing you have told me has worked I need to talk with you.", create_thread())
