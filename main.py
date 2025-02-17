import os
import sys
from dotenv import load_dotenv
import panel as pn

#from dotenv import load_dotenv # Import the load_dotenv function from the dotenv module when running locally
#load_dotenv() # Load environment variables from the .env file when running locally

pn.extension(theme='default')

DATA_DIR = os.path.join(os.getenv('HOME', '/home'), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from src.latest_ai_development.crew import LatestAiDevelopment
from src.latest_ai_development.crew import chat_interface
import threading

from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin
import time

def custom_ask_human_input(self, final_answer: dict) -> str:

    global user_input

    chat_interface.send(final_answer, user="Assistant", respond=False)

    prompt = "Please provide feedback on the Final Result and the Agent's actions: "
    chat_interface.send(prompt, user="System", respond=False)

    while user_input == None:
        time.sleep(1)

    human_comments = user_input
    user_input = None

    return human_comments

CrewAgentExecutorMixin._ask_human_input = custom_ask_human_input

user_input = None
crew_started = False

def initiate_chat(message):
    global crew_started
    crew_started = True

    try:
        # Initialize crew with inputs
        inputs = {"topic": message}
        crew = LatestAiDevelopment().crew()
        result = crew.kickoff(inputs=inputs)

        # Send results back to chat
    except Exception as e:
        chat_interface.send(f"An error occurred: {e}", user="Assistant", respond=False)
    crew_started = False

def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global crew_started
    global user_input

    if not crew_started:
        thread =  threading.Thread(target=initiate_chat, args=(contents,))
        thread.start()
    
    else:
        user_input = contents

chat_interface.callback = callback

# Send welcome message
chat_interface.send(
    "Welcome! My name is Paulch, your research assistant. What topic would you like to know more about?",
    user="Assistant",
    respond=False
)

# Make it servable
chat_interface.servable()

