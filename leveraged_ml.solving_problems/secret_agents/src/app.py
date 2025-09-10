from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from llm.llm_interface import send_to_llm
from utils.tool_executor import execute_tool
from utils.mission_log import load_mission_log, save_mission_log

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("message")
def handle_message(message):
    # TODO: Send user message to the LLM and perform the necessary actions after receiving the response.
    # TODO: Update mission log
    return


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
