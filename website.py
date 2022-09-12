from flask import Flask
from threading import Thread
from waitress import serve
import logging


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
    

app = Flask('')

@app.route('/')
def home():
    return "Hello. I am alive!"

@app.route("/ballottoc")
def toc():
    return """
    By participating in the ballot, you agree to the following:<br>

    Frank Liu (I) can revoke your vote at any moment<br>
    I can question the integrity of your vote at any time<br>
    You will not attempt to illegally influence the vote<br>
    You have not influenced others to sacrifice the integrity of the vote<br>
    You affirm that your vote is your vote, and nobody else's<br>
    You agree that I can change these rules at my discretion given the circumstances<br>
    """

def run():
  serve(app, host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()