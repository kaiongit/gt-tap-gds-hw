from urllib.parse import urlparse, ParseResult
from flask import Flask, render_template, redirect, url_for
from flask import request as frequest
import json
import requests

app = Flask(__name__)

shrunk = []

@app.route("/", methods=["POST", "GET"])
def root():
    if frequest.method == "GET":
        return render_template("index.html")
 
    payload = json.dumps( {"url": frequest.form["inputUrl"]} )
    response = invoke_shrink_api(payload)
    
    response_dict = json.loads(response.text)
    response_short = response_dict["short"]
    short_url = frequest.host_url + response_short
    response_dict["short"] = short_url

    shrunk.insert(0, response_dict)

    return render_template("index.html", shrunk=shrunk)

def invoke_shrink_api(payload: str) -> requests.Response:
    url = "https://asia-southeast2-nomadic-thinker-355706.cloudfunctions.net/url-shrinker-function"
    headers = {
        "Content-Type": "application/json"
    }   

    return requests.request("POST", url, headers=headers, data=payload)
    

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)    