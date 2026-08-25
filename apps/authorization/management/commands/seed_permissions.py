from django.core.management.base import BaseCommand

from apps.authorization.models import Permission
from apps.authorization.permissions import PERMISSION_CATALOG


class Command(BaseCommand):

    help = "Create missing permissions from the permission catalog."

    def handle(self, *args, **options):

        created_count = 0
        existing_count = 0

        for code, data in PERMISSION_CATALOG.items():

            permission = Permission.objects(
                code=code
            ).first()

            if permission:
                existing_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Already exists: {code}"
                    )
                )

                continue

            Permission(
                code=code,
                name=data["name"],
                description=data["description"],
                module=data["module"],
                is_active=True,
            ).save()

            created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {code}"
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