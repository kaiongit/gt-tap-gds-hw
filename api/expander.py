from flask import jsonify, make_response
from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference

import functions_framework

# add docs please
# add types to variable
# change value errors to just numbers

@functions_framework.http
def expand_url_http(request):

    content_type = request.headers["content-type"]

    if content_type != "application/json":
        raise ValueError("Unknown content type: {}".format(content_type))
        
    request_json = request.get_json(silent=True)

    if not (request_json) or not ("short" in request_json):
        raise ValueError("JSON is invalid, or missing a 'short' property")

    short = request_json["short"]

    db = firestore.Client(project="nomadic-thinker-355706")
    col_ref: CollectionReference = db.collection("urls")

    doc = get_doc_or_none(col_ref, short)

    if not doc:
        return code_only_error(404)
    else:
        long = doc.to_dict()["url"]

    return jsonify({
        "short": short,
        "long": long        
    })

def code_only_error(status_code: int):
    return make_response("", status_code)

def get_doc_or_none(col_ref: CollectionReference, short: str) -> DocumentSnapshot:
    docs = col_ref.where("short", "==", short).limit(1).get()
    return docs[0] if len(docs) > 0 else None
