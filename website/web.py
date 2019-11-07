import sys
sys.path.append("..")
from io import StringIO
from modiscript.utils import ErrorHandler
from modiscript.api import ModiScript
from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

ms = ModiScript()
orignal_stdout = sys.stdout
orignal_stdin = sys.stdin


def captureOutput(func):
    def inner(*args, **kwargs):
        sys.stdout = StringIO()

        func(*args, **kwargs)

        out = sys.stdout.getvalue()
        sys.stdout = orignal_stdout
        return out
    return inner


@captureOutput
def execute(code, stdin=None):
    if stdin:
        sys.stdin = StringIO(str(stdin))
    ms.execute(code, "code")
    sys.stdin = orignal_stdin


@app.route("/", methods=["POST"])
def run():
    body = request.get_json(silent=True)
    code = body.get("code")
    stdin = body.get("stdin")
    if not code:
        return jsonify({"error": "Executable code has not been provided."}), 400

    try:
        return jsonify({"out": execute(code, stdin)}), 200
    except ErrorHandler as e:
        return jsonify({"error": str(e)}), 402
