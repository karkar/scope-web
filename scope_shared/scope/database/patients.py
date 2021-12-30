import re
from typing import List, Optional

import pymongo
import pymongo.database
import pymongo.results

PATIENTS_COLLECTION_NAME = "patients"


def create_patient_collection(
    *, database: pymongo.database.Database, patient: dict
) -> str:
    """
    Initialize a patient collection.

    Initialize the collection with multiple subchema documents and return the collection name.
    """

    identity = patient["identity"]
    profile = patient["profile"]
    clinical_history = patient["clinicalHistory"]
    values_inventory = patient["valuesInventory"]

    patient_collection_name = "patient_{}".format(identity["_id"])

    # Get or create a patients collection
    patients_collection = database.get_collection(patient_collection_name)

    # Ensure an identity document exists.
    result = patients_collection.find_one(
        filter={
            "type": "identity",
        }
    )
    if result is None:
        # NOTE: Talk to James about this.
        patients_collection.insert_one(document=identity)
        patients_collection.insert_one(document=profile)
        patients_collection.insert_one(document=clinical_history)
        patients_collection.insert_one(document=values_inventory)

    # Create unique index on (`type`, `v`)
    patients_collection.create_index(
        [("type", pymongo.ASCENDING), ("v", pymongo.DESCENDING)], unique=True
    )

    return patient_collection_name


def create_patient(
    *, database: pymongo.database.Database, patient: dict
) -> pymongo.results.InsertOneResult:
    """
    Create the provided patient.
    """

    # TODO: Verify schema against patient

    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    result = collection.insert_one(document=patient)

    return result


def delete_patient(
    *, database: pymongo.database.Database, id: str
) -> pymongo.results.DeleteResult:
    """
    Delete "patient" document with provided id.
    """

    # TODO: Verify schema against patient

    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    query = {
        "type": "patient",
        "_id": id,
    }

    result = collection.delete_one(filter=query)

    return result


def get_patient(*, database: pymongo.database.Database, id: str) -> Optional[dict]:
    """
    Retrieve "patient" document with provided id.
    """
    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    query = {
        "type": "patient",
        "_id": id,
    }

    patient = collection.find_one(filter=query)

    # TODO: Verify schema against patient

    return patient


# NOTE: This method will go away eventually.
def get_patients(*, database: pymongo.database.Database) -> List[dict]:
    """
    Retrieve all "patient" documents.
    """
    collection = database.get_collection(name=PATIENTS_COLLECTION_NAME)

    query = {
        "type": "patient",
    }

    cursor = collection.find(filter=query)
    patients = list(cursor)

    # To serialize object, convert _id in document to string.
    for doc in patients:
        doc.update((k, str(v)) for k, v in doc.items() if k == "_id")

    # TODO: Verify schema against each patient in patients

    return patients


def get_all_patients(*, database: pymongo.database.Database):
    """
    Retrieve all "patient" documents.
    """
    collections = database.list_collection_names()

    # Patient collection names start with `patient_`
    regex_match_string = "patient_(.*)"
    patient_collections = [
        collection
        for collection in collections
        if re.match(regex_match_string, collection)
    ]

    patients = []

    for patient_collection in patient_collections:
        patient = {"type": "patient"}

        collection = database.get_collection(name=patient_collection)
        queries = [
            {
                "type": "identity",
            },
            {
                "type": "profile",
            },
            {
                "type": "clinicalHistory",
            },
            {
                "type": "valuesInventory",
            },
        ]

        for query in queries:
            # Find the document with highest `v`.
            found = collection.find_one(filter=query, sort=[("v", pymongo.DESCENDING)])
            # To serialize object and to avoid `TypeError: Object of type ObjectId is not JSON serializable` error, convert _id in document to string.
            if "_id" in found:
                found["_id"] = str(found["_id"])
            patient[query["type"]] = found

        patients.append(patient)

    return patients
