import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

cred = credentials.Certificate('../../bscpe-80d73-4c68844c57fc.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()

def addData(col_name, data, doc_name=""):
    if not doc_name:
        db.collection(col_name).add(data)
        return
    
    db.collection(col_name).document(doc_name).set(data)

