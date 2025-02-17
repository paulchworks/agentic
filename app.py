import os
import sys
from flask import Flask, request, jsonify, render_template
from threading import Thread, Lock
from src.latest_ai_development.crew import LatestAiDevelopment
from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin
import time

# Initialize Flask app
app = Flask(__name__)

# Constants and configurations
DATA_DIR = os.path.join(os.getenv('HOME', '/home'), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Global variables for managing state
user_input = None
crew_started = False
lock = Lock()

# Custom method for asking human input
def custom_ask_human_input(self, final_answer: dict) -> str:
    global user_input
    # Send the assistant's response to the frontend
    send_message_to_frontend(final_answer, "Assistant")
    prompt = "Please provide feedback on the Final Result and the Agent's actions: "
    send_message_to_frontend(prompt, "System")
    
    # Wait for user input
    while user_input is None:
        time.sleep(1)
    human_comments = user_input
    user_input = None
    return human_comments

CrewAgentExecutorMixin._ask_human_input = custom_ask_human_input

# Function to initiate the chat process
def initiate_chat(message):
    global crew_started
    crew_started = True
    try:
        # Initialize crew with inputs
        inputs = {"topic": message}
        crew = LatestAiDevelopment().crew()
        result = crew.kickoff(inputs=inputs)
        # Send results back to the frontend
        send_message_to_frontend(result, "Assistant")
    except Exception as e:
        send_message_to_frontend(f"An error occurred: {e}", "Assistant")
    finally:
        crew_started = False

# Function to send messages to the frontend (via a global queue or similar mechanism)
def send_message_to_frontend(message, user):
    # In a real-world scenario, this would push the message to a WebSocket or similar real-time communication channel.
    # For simplicity, we'll use a global list to simulate this behavior.
    global message_queue
    message_queue.append({"user": user, "message": message})

# Flask route to serve the chat interface
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle incoming chat messages
@app.route('/chat', methods=['POST'])
def chat():
    global user_input
    global crew_started
    data = request.json
    message = data.get("message")

    with lock:
        if not crew_started:
            thread = Thread(target=initiate_chat, args=(message,))
            thread.start()
        else:
            user_input = message  # Store user input for the ongoing conversation

    return jsonify({"status": "success"})

# Flask route to fetch messages for the frontend
@app.route('/messages', methods=['GET'])
def get_messages():
    global message_queue
    messages = message_queue
    message_queue = []  # Clear the queue after sending messages
    return jsonify(messages)

# Initialize a global message queue
message_queue = []

if __name__ == '__main__':
    app.run(debug=True)