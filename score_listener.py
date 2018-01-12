from flask import Flask, request

from score import SetLights


app = Flask(__name__)

PREV_SCORE = 0

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/score')
def score():
    global PREV_SCORE
    score = request.args.get('score', default=0, type=int)
    if score != 0:
        PREV_SCORE = score
        lights = SetLights()
        adj_score = lights.adjust_score(score, lights.max_score, lights.strip.numPixels())
        lights.animate_score(score)
    return str(PREV_SCORE)
