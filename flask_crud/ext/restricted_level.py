from flask_login import current_user, login_required
from flask_crud.components import List, Create, Read, Update, Delete


class RestrictedList(List):
    decorators = [login_required]


class RestrictedCreate(Create):
    decorators = [login_required]


class RestrictedRead(Read):
    decorators = [login_required]


class RestrictedUpdate(Update):
    decorators = [login_required]


class RestrictedDelete(Delete):
    decorators = [login_required]


class RestrictedMixin:
    components = (
        RestrictedList,
        RestrictedCreate,
        RestrictedRead,
        RestrictedUpdate,
        RestrictedDelete,
    )

    def get_roles(self):
        # list(map(operator.itergetter(1), root))[1:] -> all roles
        user_roles = current_user.get_roles()
        roles = super().get_roles()
        return {
            key: list(set(values) & set(user_roles))
            for key, values in roles.items()
        }
