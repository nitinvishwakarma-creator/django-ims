from django.core.management.base import BaseCommand

from apps.authorization.models import Role, Permission
from apps.authorization.roles import ROLE_CATALOG
from apps.accounts.models import User


class Command(BaseCommand):

    help = "Create default roles for an organization."

    def add_arguments(self, parser):
        parser.add_argument(
            "--organization",
            required=True,
            help="Organization ID",
        )

    def handle(self, *args, **options):

        organization_id = options["organization"]

        user = User.objects(
            organization=organization_id
        ).first()

        if not user:
            self.stdout.write(
                self.style.ERROR(
                    "No user found for this organization."
                )
            )
            return

        organization = user.organization

        if not organization:
            self.stdout.write(
                self.style.ERROR(
                    "User does not belong to an organization."
                )
            )
            return

        created_count = 0
        existing_count = 0

        for key, data in ROLE_CATALOG.items():

            role = Role.objects(
                organization=organization,
                name=data["name"],
            ).first()

            if role:

                permissions = []

                for permission_code in data["permissions"]:

                    permission = Permission.objects(
                        code=permission_code,
                        is_active=True,
                    ).first()

                    if not permission:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Permission not found: {permission_code}"
                            )
                        )
                        continue

                    permissions.append(permission)

                role.description = data["description"]
                role.permissions = permissions
                role.save()

                existing_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Updated: {data['name']}"
                    )
                )

                continue

            permissions = []

            for permission_code in data["permissions"]:

                permission = Permission.objects(
                    code=permission_code
                ).first()

                if not permission:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Permission not found: {permission_code}"
                        )
                    )
                    continue

                permissions.append(permission)

            Role(
                organization=organization,
                name=data["name"],
                description=data["description"],
                permissions=permissions,
            ).save()

            created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {data['name']}"
                )
            )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created_count}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Already existed: {existing_count}"
            )
        )