from flask_login import current_user, login_required


class RestrictedMixin:
    decorators = [login_required]

    def get_roles(self):
        # list(map(operator.itergetter(1), root))[1:] -> all roles
        user_roles = current_user.get_roles()
        roles = super().get_roles()
        return {
            key: list(set(values) & set(user_roles))
            for key, values in roles.items()
        }
