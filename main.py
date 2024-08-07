# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request
from faster_whisper import WhisperModel
import base64
import os

# os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# model = WhisperModel("small.en", device="cpu", compute_type="int8")

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

@app.route("/transcribe", methods=["POST"])
def transcribe():
    # encode_string = base64.b64encode(open("audio.wav", "rb").read())
    wav_file = open("./test.m4a", "wb")
    decode_string = base64.b64decode(request.json["file"])
    wav_file.write(decode_string)
    print("saved")

    # segments, info = model.transcribe("test.m4a", beam_size=5, language="en", vad_filter=True)
    print("crossed")
    full_text = ""

    # for segment in segments:
        # full_text += segment.text + " "
        
    print(full_text)


    return full_text

# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(host="0.0.0.0",port=55001)