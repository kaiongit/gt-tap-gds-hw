from flask import jsonify
from random_words import RandomWords
from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference
from urllib.parse import quote

import functions_framework

# add docs please
# add types to variable

@functions_framework.http
def shrink_url_http(request):

    content_type: str = request.headers["content-type"]

    if content_type != "application/json":
        raise ValueError("Unknown content type: {}".format(content_type))
        
    request_json = request.get_json(silent=True)

    if not (request_json) or not ("url" in request_json):
        raise ValueError("JSON is invalid, or missing a 'url' property")

    url = request_json["url"]

    db = firestore.Client(project="nomadic-thinker-355706")
    col_ref: CollectionReference = db.collection("urls")

    doc_name = make_document_name(url)

    doc = get_doc_or_none(col_ref, doc_name)

    if doc:
        short = doc.to_dict()["short"]
    else:
        short = set_new_doc(col_ref, doc_name, url)

    return jsonify({
        "long": url,
        "short": short,
        "exist": (doc is not None)
        })

def make_document_name(url: str) -> str:
    s = quote(url)
    s2 = s.replace("/", "")
    return s2

def set_new_doc(col_ref: CollectionReference, doc_name: str, url: str) -> str:
    doc_ref = col_ref.document(doc_name)

    existing_short = True
    one_word = ""

    while existing_short:
        words = RandomWords().random_words(count=2)
        words = [word.title() for word in words]
        one_word = "".join(words)

        existing_short = short_exists(col_ref, one_word)

    doc_ref.set({
        "url": url,
        "short": one_word
    })

    return one_word

def short_exists(col_ref: CollectionReference, short: str) -> bool:
    docs = col_ref.where("short", "==", short).limit(1).get()
    return len(list(docs)) > 0

def get_doc_or_none(col_ref: CollectionReference, doc_name:str) -> DocumentSnapshot:
    doc_ref = col_ref.document(doc_name)

    doc = doc_ref.get()
    return doc if doc.exists else None
