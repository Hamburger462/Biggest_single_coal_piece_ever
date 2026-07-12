import os

import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "..", "..", "bscpe-80d73-4c68844c57fc.json")

cred = credentials.Certificate(CREDENTIALS_PATH)

app = firebase_admin.initialize_app(cred)

db = firestore.client()


def addDoc(col_name, data):
    db.collection(col_name).add(data)


def setDoc(col_name, doc_name, data):
    db.collection(col_name).document(doc_name).set(data)


def getDoc(col_name, doc_name):
    return db.collection(col_name).document(doc_name).get()


def getDocs(col_name, doc_name):
    return db.collection(col_name).get()