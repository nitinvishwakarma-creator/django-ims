from datetime import datetime

from mongoengine import (
    Document,
    EmailField,
    StringField,
    BooleanField,
    DateTimeField,
)


class Organization(Document):
    name = StringField(
        required=True,
        max_length=200,
    )

    email = EmailField(
        required=True,
    )

    phone = StringField(
        max_length=30,
    )

    address = StringField(
        max_length=500,
    )

    country = StringField(
        max_length=100,
        default="India",
    )

    currency = StringField(
        max_length=10,
        default="INR",
    )

    timezone = StringField(
        max_length=100,
        default="Asia/Kolkata",
    )

    is_active = BooleanField(
        default=True,
    )

    created_at = DateTimeField(
        default=datetime.utcnow,
    )

    updated_at = DateTimeField(
        default=datetime.utcnow,
    )

    meta = {
        "collection": "organizations",
    }