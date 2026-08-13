class AuthorizationService:

    @staticmethod
    def has_permission(user, permission_code):
        if not user:
            return False

        if not user.is_active:
            return False

        if not user.role:
            return False

        for permission in user.role.permissions:
            if permission.code == permission_code and permission.is_active:
                return True

        return False