import os

from mongoengine import connect


def connect_to_mongodb():
    """
    Establish a connection between Django and MongoDB Atlas.
    """

    uri = os.getenv("MONGODB_URI")
    database = os.getenv("MONGODB_DATABASE", "ims_db")

    if not uri:
        raise ValueError("MONGODB_URI is not configured.")

    connect(
        alias="default",
        db=database,
        host=uri,
    )