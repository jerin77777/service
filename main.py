# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request

from scipy import cluster
import pandas as pd
import math
import requests
import cv2
import matplotlib.pyplot as plt
from inference_sdk import InferenceHTTPClient
import base64
import json

def rgb2hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def get_color_pallete(input_file, num_colors):
    img = plt.imread(input_file)

    red, green, blue = [], [], []
    for line in img:
        for pixel in line:
            r, g, b = pixel
            red.append(r)
            green.append(g)
            blue.append(b)

    df = pd.DataFrame({
        'red': red,
        'green': green,
        'blue': blue
    })

    df['standardized_red'] = cluster.vq.whiten(df['red'])
    df['standardized_green'] = cluster.vq.whiten(df['green'])
    df['standardized_blue'] = cluster.vq.whiten(df['blue'])

    color_pallete, distortion = cluster.vq.kmeans(df[['standardized_red', 'standardized_green', 'standardized_blue']],
                                                num_colors)
    colors = []
    red_std, green_std, blue_std = df[['red', 'green', 'blue']].std()
    for color in color_pallete:
        scaled_red, scaled_green, scaled_blue = color
        colors.append((
            math.ceil(scaled_red * red_std),
            math.ceil(scaled_green * green_std),
            math.ceil(scaled_blue * blue_std)
        ))


    final_colors = []

    for color in colors:
        final_colors.append(rgb2hex(color[0], color[1], color[2]))

    return final_colors


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

@app.route("/get_pallet", methods=["POST"])
def get_pallet():

    url = f"https://api.freepik.com/v1/resources?term={request.json['subject']}&page=1&limit=1&filters[content_type][photo]=1"

    headers = {
        "Accept-Language": "<accept-language>",
        "x-freepik-api-key": "FPSXd4370660d2f441ea9db1508cfae125e7"
    }

    response = requests.request("GET", url, headers=headers)
    print(response.json()["data"][0]["image"]["source"]["url"])

    bytes = requests.get(response.json()["data"][0]["image"]["source"]["url"]).content

    f = open("img.jpg", "wb")
    f.write(bytes)
    f.close()

    image = cv2.imread('img.jpg')
    h, w = image.shape[:2]
    aspect_ratio = w / h

    resized_image = cv2.resize(image, (200, int(200 / aspect_ratio)))

    cv2.imwrite("img.jpg", resized_image)

    colors_list = get_color_pallete("./img.jpg", 10)

    colors_list

    return str(colors_list)

@app.route("/get_predictions", methods=["POST"])
def get_predictions():

    with open("./design.jpg", "wb") as fh:
        fh.write(base64.b64decode(request.json["image"]))

    CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="vkbPyTkNkozqQgf6i4i0"
    )

    result = CLIENT.infer("./design.jpg", model_id="detector_meme/2")

    return json.dumps(result)

if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(host="0.0.0.0",port=55001)