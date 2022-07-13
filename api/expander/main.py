from flask import jsonify
from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference

GCLOUD_PROJECT_NAME: str = "nomadic-thinker-355706"

import functions_framework  # Only for local development, do not include in deployment

@functions_framework.http # Only for local development, do not include in deployment
def expand_url_http(request):

    # Complain if payload is not JSON
    try:
        content_type: str = request.headers["content-type"]
    except KeyError:
        return jsonify({"msg": "Unknown payload type"}), 400

    if content_type != "application/json":
        return jsonify({"msg": "Unknown payload type"}), 400
        
    # Complain if payload does not contain "short" property
    request_json: dict = request.get_json(silent=True)
    if not (request_json) or not ("short" in request_json):
        return jsonify({"msg": "Payload is invalid, or does not contain property 'short'"}), 400

    # Check DB if document exists
    db: firestore.Client = firestore.Client(project=GCLOUD_PROJECT_NAME)
    col_ref: CollectionReference = db.collection("urls")

    short: str = request_json["short"]

    doc: DocumentSnapshot = get_doc_or_none(col_ref, short)

    # If document does not exists, return
    if not doc:
        return jsonify({"msg": "Cannot find document"}), 404

    # If document exists, return 200
    else:
        doc_dict: dict = doc.to_dict()
        long: str = doc_dict["url"]
        seen: int = doc_dict["seen"]

        return jsonify({
            "short": short,
            "long": long,
            "seen": seen
        }), 200

def get_doc_or_none(col_ref: CollectionReference, short: str) -> DocumentSnapshot:
    """
    Turns a hyperlink into a Firestore compliant document name by percent encoding then removing
    forward slashes

    Parameters
    ----------
    col_ref: CollectionReference
        The reference to the collection to check in
    short: str
        The short path to check

    Return
    ------
    The document or None
    """
    docs = col_ref.where("short", "==", short).limit(1).get()
    return docs[0] if len(docs) > 0 else None
