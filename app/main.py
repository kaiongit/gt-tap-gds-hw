import json
from urllib.parse import ParseResult, urlparse

import requests
from flask import Flask, redirect, render_template
from flask import request as frequest
from flask import url_for

app = Flask(__name__)

shrunk: dict = []

@app.route("/", methods=["POST", "GET"])
def root():

    # If requst method is GET
    if frequest.method == "GET":
        return render_template("index.html")
 
    # If request method is POST
    payload: str = json.dumps( {"url": frequest.form["inputUrl"]} )
    response: requests.Response = invoke_shrink_api(payload)
    
    # Complain if request failed
    if response.status_code not in (200, 201):
        return render_template("index.html", error=True)

    response_dict: dict = json.loads(response.text)
    response_short: str = response_dict["short"]
    short_url: str = frequest.host_url + response_short
    response_dict["short"] = short_url

    shrunk.insert(0, response_dict)

    return render_template("index.html", shrunk=shrunk)

@app.errorhandler(404)
def not_found(e):
    short: str = frequest.url.split("/")[-1]
    payload: str = json.dumps( {"short": short} )
    response: requests.Response = invoke_expand_api(payload)

    # If given path is previously shortened
    if response.status_code == 200:
        response_dict: dict = json.loads(response.text)
        response_long: str = response_dict["long"]

        # Parse url into proper redirectable url
        urlp: ParseResult = urlparse(response_long, "http")
        if not urlp.netloc:
            urlp = urlp._replace(netloc=urlp.path)
            urlp = urlp._replace(path="")

        return redirect(urlp.geturl(), 302)

    # If given path is not previously shortened, quietly redirect to root
    else:
        return redirect(url_for(".root"))

def invoke_shrink_api(payload: str) -> requests.Response:
    """
    Invokes the URL shrinker API

    Parameters
    ----------
    payload: str
        The payload to send to the API

    Return
    ------
    The response of the invocation
    """
    url: str = "https://asia-southeast2-nomadic-thinker-355706.cloudfunctions.net/url-shrinker-function"
    headers: dict = {
        "Content-Type": "application/json"
    }   

    return requests.request("POST", url, headers=headers, data=payload)

def invoke_expand_api(payload: str) -> requests.Response:
    """
    Invokes the URL expander API

    Parameters
    ----------
    payload: str
        The payload to send to the API

    Return
    ------
    The response of the invocation
    """
    url: str = "https://asia-southeast2-nomadic-thinker-355706.cloudfunctions.net/url-expand-function"
    headers: dict = {
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
