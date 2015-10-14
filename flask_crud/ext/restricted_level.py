from flask_login import current_user, login_required

from flask_crud.crud import Crud
from flask_crud.components import List, Create, Read, Update, Delete


class LoginRequiredList(List):
    decorators = [login_required]


class LoginRequiredCreate(Create):
    decorators = [login_required]


class LoginRequiredRead(Read):
    decorators = [login_required]


class LoginRequiredUpdate(Update):
    decorators = [login_required]


class LoginRequiredDelete(Delete):
    decorators = [login_required]



class RestrictedCrud(Crud):
    COMPONENTS = [List, Read, Create, Update, Delete]

    def get_roles(self):
        all_roles = super().get_roles()
        # user.roles() return a dict with crud names as keys, and a list
        # with component names as value for each key
        # eg: {'post': ('create', 'edit', 'update', 'delete')}
        try:
            user_roles = current_user().roles()[self.absolute_name]
        except KeyError:
            return all_roles
        return [
            (name, endpoint) for name, endpoint in all_roles
            if name in user_roles
        ]

