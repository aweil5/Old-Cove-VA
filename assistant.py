
import openai
from dotenv import load_dotenv
import time
import logging
from datetime import datetime
import os

load_dotenv()
# openai.api_key = os.environ.get("OPENAI_API_KEY")
# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:
# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )

client = openai.OpenAI()

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
    # ==== Steps --- Logs ==
    # run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
    # print(f"Steps---> {run_steps.data[0]}")

    # DO NOT NEED WHILE OR TRY SINCE HANDLED BY WAIT_FOR_RUN_COMPLETION
    # run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    # if run.completed_at:
    #     messages = client.beta.threads.messages.list(thread_id=thread_id)
    #     last_message = messages.data[0]
    #     response = last_message.content[0].text.value
    #     return response
    # else:
    #     return "ERROR"




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
                print(f"Run completed in {formatted_elapsed_time}")
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


































# def main():
#     thread_id = "thread_ov3LJSohjBb22TQJiDjq2OSh"
#     print("Calling func")
#     print(help_user("My lurtron dimmer is not working, how do i fix it?", thread_id))

# main()


# # ==  Create our Assistant (Uncomment this to create your assistant) ==
# personal_trainer_assis = client.beta.assistants.create(
#     name="Personal Trainer",
#     instructions="""You are the best personal trainer and nutritionist who knows how to get clients to build lean muscles.\n
#      You've trained high-caliber athletes and movie stars. """,
#     model=model,
# )
# asistant_id = personal_trainer_assis.id
# print(asistant_id)


# === Thread (uncomment this to create your Thread) ===
# thread = client.beta.threads.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "How do I get started working out to lose fat and build muscles?",
#         }
#     ]
# )
# thread_id = thread.id
# print(thread_id)