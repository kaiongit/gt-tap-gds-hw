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
    
    if response.status_code not in (200, 201):
        return render_template("index.html", error=True)

    response_dict = json.loads(response.text)
    response_short = response_dict["short"]
    short_url = frequest.host_url + response_short
    response_dict["short"] = short_url

    shrunk.insert(0, response_dict)

    return render_template("index.html", shrunk=shrunk)

@app.errorhandler(404)
def not_found(e):
    short = frequest.url.split("/")[-1]
    payload = json.dumps( {"short": short} )
    response = invoke_expand_api(payload)

    if response.status_code == 200:
        response_dict = json.loads(response.text)
        response_long = response_dict["long"]

        urlp = urlparse(response_long, "http")
        if not urlp.netloc:
            urlp = urlp._replace(netloc=urlp.path)
            urlp = urlp._replace(path="")

        return redirect(urlp.geturl(), 302)
    else:
        return redirect(url_for(".root"))

def invoke_shrink_api(payload: str) -> requests.Response:
    url = "https://asia-southeast2-nomadic-thinker-355706.cloudfunctions.net/url-shrinker-function"
    headers = {
        "Content-Type": "application/json"
    }   

    return requests.request("POST", url, headers=headers, data=payload)

def invoke_expand_api(payload: str) -> requests.Response:
    url = "https://asia-southeast2-nomadic-thinker-355706.cloudfunctions.net/url-expand-function"
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