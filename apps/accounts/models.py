from datetime import datetime

from django.contrib.auth.hashers import make_password, check_password

from mongoengine import (
    Document,
    EmailField,
    StringField,
    BooleanField,
    DateTimeField,
    ReferenceField,
)
from apps.organizations.models import Organization
from apps.authorization.models import Role
class User(Document):
    role = ReferenceField(Role,required=False)
    organization = ReferenceField(Organization,required=True,)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)

    first_name = StringField(required=True, max_length=100)
    last_name = StringField(required=True, max_length=100)

    is_active = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection":
            "users",

        "indexes": [
            "organization",
            "role",

            {
                "fields": [
                    "organization",
                    "is_active",
                ],
            },

            {
                "fields": [
                    "organization",
                    "created_at",
                ],
            },
        ],
    }

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    def has_permission(self, permission_code):
        from apps.authorization.services import AuthorizationService

        return AuthorizationService.has_permission(
            self,
            permission_code,
        )

    @property
    def is_authenticated(self):
        return True


    @property
    def is_anonymous(self):
        return False


    def get_username(self):
        return self.email


    def get_session_auth_hash(self):
        return self.password