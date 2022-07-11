from urllib.parse import quote

from flask import jsonify
from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference
from random_words import RandomWords

GCLOUD_PROJECT_NAME: str = "nomadic-thinker-355706"

import functions_framework  # Only for local development, do not include in deployment

@functions_framework.http # Only for local development, do not include in deployment
def shrink_url_http(request):

    # Complain if payload is not JSON
    try:
        content_type: str = request.headers["content-type"]
    except KeyError:
        return jsonify({"msg": "Unknown payload type"}), 400

    if content_type != "application/json":
        return jsonify({"msg": "Unknown payload type"}), 400
        
    # Complain if payload does not contain "url" property
    request_json = request.get_json(silent=True)
    if not (request_json) or not ("url" in request_json):
        return jsonify({"msg": "Payload is invalid, or does not contain property 'url'"}), 400

    # Check DB if document already exist
    db: firestore.Client = firestore.Client(project=GCLOUD_PROJECT_NAME)
    col_ref: CollectionReference = db.collection("urls")

    url: str = request_json["url"]
    doc_name: str = make_document_name(url)

    doc: DocumentSnapshot = get_doc_or_none(col_ref, doc_name)

    # If document already exist, return 200
    if doc:
        short: str = doc.to_dict()["short"]
        return jsonify({
            "long": url,
            "short": short,
            "exist": True
            }), 200

    # If document does not exist, create and return 201
    else:
        short: str = set_new_doc(col_ref, doc_name, url)
        return jsonify({
            "long": url,
            "short": short,
            "exist": False
            }), 201

def make_document_name(url: str) -> str:
    """
    Turns a hyperlink into a Firestore compliant document name by percent encoding then removing
    forward slashes

    Parameters
    ----------
    url: str
        The hyperlink to convert

    Return
    ------
    The converted document name
    """
    s = quote(url)
    s2 = s.replace("/", "")
    return s2

def set_new_doc(col_ref: CollectionReference, doc_name: str, url: str) -> str:
    """
    Generates a shortened path, creates a document in Firestore, and sets its properties

    Parameters
    ----------
    col_ref: CollectionReference
        The reference to the collection to create the document
    doc_name: str
        The name of the document
    url: str
        The value for the 'url' property

    Return
    ------
    The shortened (shrunken) path
    """
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
    """
    Check if a short path already exists in any document in the collection

    Parameters
    ----------
    col_ref: CollectionReference
        The reference to the collection to check in
    short: str
        The short path to check

    Return
    ------
    If the short path already exists
    """
    docs = col_ref.where("short", "==", short).limit(1).get()
    return len(list(docs)) > 0

def get_doc_or_none(col_ref: CollectionReference, doc_name:str) -> DocumentSnapshot:
    """
    Retrieve a document from the collection

    Parameters
    ----------
    col_ref: CollectionReference
        The reference to the collection to retrieve from
    doc_name: str
        The name of the document to retrieve

    Return
    ------
    The document or None
    """
    doc_ref = col_ref.document(doc_name)

    doc = doc_ref.get()
    return doc if doc.exists else None
